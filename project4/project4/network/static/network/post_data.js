
function get_data(page_number, option, username=null) {
    // clear divs
    
    const posts = document.querySelector("#posts");
    posts.innerHTML = "";
    const pagiation_div = document.querySelector("#pagination_div");
    pagiation_div.innerHTML = "";

    if (username === null) {
        fetch_url = `/posts/${option}?page=${page_number}`
    } else {
        fetch_url = `/posts/${option}?username=${username}&page=${page_number}`
    }
    
    fetch(fetch_url)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.status);
        }
    })
    .then(json => {
        // data
        // console.log(json);
        json["posts_list"].forEach(post => {
            let post_div = document.createElement('div');
            post_div.setAttribute('class', 'post_div');

            let author_link = document.createElement('a');
            author_link.setAttribute('class', 'post_author');
            author_link.setAttribute('href', `profile/${post.author}`);
            author_link.innerText = post.author;

            let article_post = document.createElement('article');
            article_post.setAttribute('class', 'article_post');
            article_post.innerText = post.content;

            let ptag_datetime = document.createElement('p');
            ptag_datetime.setAttribute('class', 'ptag_datetime');
            ptag_datetime.innerText = post.created_at;

            let separator = document.createElement('hr');
            separator.setAttribute('class', 'separator');

            let footer_div = document.createElement('div');
            footer_div.setAttribute('class', 'fotter_post');

            let like_div = document.createElement('div');
            like_div.setAttribute('class', 'like_section');

            /*let svg_image = `<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-suit-heart-fill" viewBox="0 0 18 18">
                <path d="M4 1c2.21 0 4 1.755 4 3.92C8 2.755 9.79 1 12 1s4 1.755 4 3.92c0 3.263-3.234 4.414-7.608 9.608a.513.513 0 0 1-.784 0C3.234 9.334 0 8.183 0 4.92 0 2.755 1.79 1 4 1z"/>
            </svg>`*/

            let svg_image = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg_image.setAttribute('width', '25');
            svg_image.setAttribute('height', '25');
            svg_image.setAttribute('fill', 'currentColor');
            svg_image.setAttribute('class', 'bi bi-suit-heart-fill');
            svg_image.setAttribute('viewBox', '0 0 18 18');

            let svg_path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            svg_path.setAttribute('d', 'M4 1c2.21 0 4 1.755 4 3.92C8 2.755 9.79 1 12 1s4 1.755 4 3.92c0 3.263-3.234 4.414-7.608 9.608a.513.513 0 0 1-.784 0C3.234 9.334 0 8.183 0 4.92 0 2.755 1.79 1 4 1z');
            svg_image.appendChild(svg_path);
            
            let span_tag = document.createElement('span');
            span_tag.setAttribute('class', 'likes');
            span_tag.textContent = post.like_count;

            let action_div = document.createElement("div");
            action_div.setAttribute('class', 'action_div'); 

            let anchor_edit = document.createElement("a");
            anchor_edit.setAttribute("class", "edit-post");
            anchor_edit.setAttribute("href", "#");
            anchor_edit.innerText = 'Edit';
            let anchor_reply = document.createElement("a");
            anchor_reply.setAttribute("href", "#");
            anchor_reply.innerText = 'Reply';
            
            if (post.author === json.user) action_div.appendChild(anchor_edit);
            action_div.appendChild(anchor_reply);


            post_div.appendChild(author_link);
            post_div.appendChild(article_post);
            post_div.appendChild(ptag_datetime);
            post_div.appendChild(separator);
            post_div.appendChild(footer_div);
            footer_div.appendChild(like_div);
            like_div.appendChild(svg_image);
            like_div.appendChild(span_tag);
            footer_div.appendChild(action_div);


            // eventListener to like a post
            svg_image.addEventListener('click', () => {
                let lastChild = like_div.lastElementChild;
                like_a_post(lastChild, post.id);
            });

            // eventListener to edit a post
            anchor_edit.addEventListener('click', event => {
                event.preventDefault();
   
                let textarea_edit = document.createElement('textarea');
                textarea_edit.setAttribute("class", "form-control");
                textarea_edit.setAttribute("name", "content");
                textarea_edit.setAttribute("required", "");
                textarea_edit.innerText = article_post.innerHTML;

                let anchor_save = document.createElement("a");
                anchor_save.setAttribute("href", "#");
                anchor_save.innerText = "Save";
                anchor_save.addEventListener('click', event => {
                    event.preventDefault();       
                    update_post(post.id, textarea_edit.value);
                    
                    article_post.innerText = textarea_edit.value;
                    textarea_edit.replaceWith(article_post);
                    anchor_cancel.replaceWith(anchor_edit);
                    anchor_save.remove();
                });
                
                let anchor_cancel = document.createElement("a");
                anchor_cancel.setAttribute("href", "#");
                anchor_cancel.innerText = 'Cancel';
                anchor_cancel.addEventListener("click", event => {
                    event.preventDefault();
                    textarea_edit.replaceWith(article_post);
                    anchor_cancel.replaceWith(anchor_edit);
                    anchor_save.remove();
                });

                article_post.replaceWith(textarea_edit);
                anchor_edit.replaceWith(anchor_save, anchor_cancel);

            });
            
            posts.appendChild(post_div);

        });

        
        /** PAGINATION */
        pagination(json);
    })
    .catch(error => console.log(error));
}

function pagination(json) {
    const pagiation_div = document.querySelector("#pagination_div");
    const max_pages_showed = 5;

    // base element, "nav" and "ul"
    let nav = document.createElement("nav");
    nav.setAttribute("id", "nav_pages");
    let ul = document.createElement("ul");
    ul.setAttribute("class", "pagination");

    nav.appendChild(ul);
    
    // previous arrow
    let li_previous = document.createElement("li");
    li_previous.innerHTML = `<a class="page-link" href="" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>`;
    if (json["has_previous"]) {
        li_previous.setAttribute("class", "page-item");
        li_previous.addEventListener('click', event => {
            event.preventDefault();
            get_data(json.previous_page, json.option);
        });
    } else {
        li_previous.setAttribute("class", "page-item disabled");
    }

    ul.appendChild(li_previous);

    // inside pages
    if (json["num_pages"] <= max_pages_showed) {
        for (let page = 1; page <= json["num_pages"]; page++) {
            let li_inside = document.createElement("li");
            if (page == json["current_page"]) {
                li_inside.setAttribute("class", "page-item active");
            } else {
                li_inside.setAttribute("class", "page-item");
            }
            li_inside.innerHTML = `<a class="page-link" href="">${page}</a>`;
            li_inside.addEventListener('click', event => {
                event.preventDefault();
                get_data(page, json.option);
            });

            ul.appendChild(li_inside);
        }
    } else {
        let page_to_the_sides = Math.trunc(max_pages_showed / 2);
        let start_page = json["current_page"] - page_to_the_sides;
        let end_page = json["current_page"] + page_to_the_sides;
        let in_end_border = end_page <= json["num_pages"] ? true: false;
        if (start_page <= 0) {
            start_page = 1;
            end_page += (max_pages_showed - end_page);
        }

        if (in_end_border) {
            for (let page = start_page; page <= end_page; page++) {
                let li_inside = document.createElement("li");
                if (page == json["current_page"]) {
                    li_inside.setAttribute("class", "page-item active");
                } else {
                    li_inside.setAttribute("class", "page-item");
                }
                li_inside.innerHTML = `<a class="page-link" href="">${page}</a>`;
                li_inside.addEventListener('click', event => {
                    event.preventDefault();
                    get_data(page, json.option);
                });
                ul.appendChild(li_inside);
            }
        } else {
            for (let page = json["num_pages"] - max_pages_showed + 1; page <= json["num_pages"]; page++) {
                let li_inside = document.createElement("li");
                if (page == json["current_page"]) {
                    li_inside.setAttribute("class", "page-item active");
                } else {
                    li_inside.setAttribute("class", "page-item");
                }
                li_inside.innerHTML = `<a class="page-link" href="">${page}</a>`;
                li_inside.addEventListener('click', event => {
                    event.preventDefault();
                    get_data(page, json.option);
                });
                ul.appendChild(li_inside);
            }
        }
    }

    // next arrow
    let li_next = document.createElement("li");
    li_next.innerHTML = `<a class="page-link" href="" aria-label="Next"><span aria-hidden="true">&raquo;</span></a>`;
    if (json["has_next"]) {
        li_next.setAttribute("class", "page-item");
        li_next.addEventListener('click', event => {
            event.preventDefault();
            get_data(json.next_page, json.option);
        });
    } else {
        li_next.setAttribute("class", "page-item disabled");
    }
    
    ul.appendChild(li_next);

    pagiation_div.appendChild(nav);
}

function like_a_post(last_child, post_id) {
    // console.log(last_child);

    fetch(`/liked_post/${post_id}`)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.status);
        }
    })
    .then(json => {
        // console.log(json);
        last_child.textContent = json.likes;
    })
    .catch(error => console.log(error));
}

function follow(username) {
    const follower = document.querySelector("#followers");
    const anchor_follow = document.querySelector("#anchor_follow");

    fetch(`/follow/${username}`)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.status);
        }
    })
    .then(json => {
        console.log(json);
        follower.innerHTML = json.follower;
        if (json.is_follower) {
            anchor_follow.innerHTML = "Unfollow?";
        } else {
            anchor_follow.innerHTML = "Follow?";
        }
    })
    .catch(error => console.log(error));
}

function update_post(post_id, content) {
    /** doc
     * https://docs.djangoproject.com/en/4.1/howto/csrf/#using-csrf-protection-with-ajax
     */
    const csrftoken = getCookie('csrftoken');
    // console.log(csrftoken);

    const request = new Request(
        `/edit_post/${post_id}`,
        {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin', // Do not send CSRF token to another domain.
            body: JSON.stringify(content)
        }
    );

    fetch(request)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response.status);
        }
    })
    .then(json => {
        console.log(json);
        
    })
    .catch(error => console.log(error));
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
