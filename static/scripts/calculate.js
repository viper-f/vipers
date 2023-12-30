async function fetch_decoded(url) {
    const response = await fetch(url)
        .then(function (response) {
            return response.arrayBuffer();
        })
        .then(function (buffer) {
            const decoder = new TextDecoder('windows-1251');
            return decoder.decode(buffer);
        });
    return response
}

async function find_last_page(subforum, user_name) {
    const parser = new DOMParser();
    let url = '/search.php?action=search&keywords=&author=' + user_name + '&forum=' + subforum + '&search_in=0&sort_dir=DESC&show_as=posts&topics=&p=1'
    const html = await fetch_decoded(url)
    const htmlDoc = parser.parseFromString(html, 'text/html')
    let last_page = 1
    const links = htmlDoc.querySelectorAll("div.pagelink a")
    if (!links || links.length === 0) {
        return last_page
    }

    links.forEach(function(link) {
        const t = link.textContent
        if (isNumeric(t) &&  parseInt(t) > last_page)
            last_page = parseInt(t)
    })
    return last_page
}

function isNumeric(str) {
    if (typeof str != "string") return false
    return !isNaN(str) && !isNaN(parseFloat(str))
}

async function get_topic_start_post(topic_id) {
    const url = '/api.php?method=topic.get&topic_id=' + topic_id + '&fields=init_post'
    const response = await fetch(url)
    const j = await response.json()
    return parseInt(j['response'][0]['init_id'])
}

function convert_date_string(date_string) {
    if (date_string.indexOf('Сегодня') !== -1) {
        const date = new Date();
        let day = date.getDate();
        let month = date.getMonth() + 1;
        let year = date.getFullYear();
        const today = `${day}-${month}-${year}`;
        date_string = date_string.replace('Сегодня', today)
    }

    if (date_string.indexOf('Вчера') !== -1) {
        const date = new Date();
        date.setDate(date.getDate() - 1);
        let day = date.getDate();
        let month = date.getMonth() + 1;
        let year = date.getFullYear();
        const yesterday = `${day}-${month}-${year}`;
        date_string = date_string.replace('Вчера', yesterday)
    }

    return date_string
}


function calculate_currency(text, currency_dict) {
    let number = text.length
    let price = 0
    let currency = ''

    for (let p of currency_dict['pricelist']) {
        if (!p['max'] && p['min'] <= number)
            price = p['price']

        if (p['min'] <= number && number <= p['max'])
            price = p['price']
    }

    if (price % 10 === 1)
        currency = currency_dict['one']
    else if (1 < price % 10 < 5)
        currency = currency_dict['two']
    else
        currency = currency_dict['five']

    return {
        'number': number,
        'price': price,
        'currency': currency
    }
}

function format_message(posts, before)
{
    let message = ''
    let total = 0
    for (let post of posts) {
        total += post['price']
        message += 'пост ' + post['number'] + ' символов — ' + post['price'] + ' ' + post['currency'] + ' [[url=' + post['href'] + ']' + post['topic_title'] + '[/url]]' + "\n"
    }
    const new_total = parseInt(before) + total
    message += 'Итого в профиле: ' + before + ' + ' + total + ' = ' + new_total
    return message
}


async function get_posts(subforums, user_name, start_time_str, currency_dict) {
    const parser = new DOMParser();
    let topics = {}
    const posts = []
    const start_time = Date.parse(start_time_str)

    for (let subforum of subforums) {
        const last_page = await find_last_page(subforum, user_name)
        let stop = false

        for (let n = 1; n <= last_page; n++) {
            if (stop) break

            const url = '/search.php?action=search&keywords=&author=' + user_name + '&forum=' + subforum + '&search_in=0&sort_dir=DESC&show_as=posts&topics=&p=' + n
            const html = await fetch_decoded(url)
            const htmlDoc = parser.parseFromString(html, 'text/html')

            for (let post of htmlDoc.querySelectorAll('div.post')) {
               const header_links = post.querySelectorAll('h3 a')

                const href = header_links[2]['href']
                const topic_title = header_links[1].text

                const post_time = Date.parse(convert_date_string(header_links[2].text))
                if (post_time < start_time) {
                    stop = true
                    break
                }

                const topic_id = parseInt(header_links[1]['href'].split('=')[1])
                if (!topics['topic_id'])
                    topics[topic_id] = await get_topic_start_post(topic_id)

                const post_id = parseInt(header_links[2]['href'].split('#p')[1])
                if (post_id !== topics[topic_id]) {

                    const text = post.querySelector('div.post-content').textContent
                    const data = calculate_currency(text, currency_dict)

                    posts.push({
                        'topic_id': topic_id,
                        'post_id': post_id,
                        'number': data['number'],
                        'href': href,
                        'topic_title': topic_title,
                        'price': data['price'],
                        'currency': data['currency']
                    })
                }
            }
        }
    }
    return posts
}