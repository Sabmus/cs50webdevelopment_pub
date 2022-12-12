document.addEventListener('DOMContentLoaded', () => {
    let username = document.querySelector("#username").textContent;
    
    try {
        let follow_link = document.querySelector("#anchor_follow");
        follow_link.addEventListener('click', event => {
            event.preventDefault();

            follow(username);

        })
      } catch (error) {
        // not log the error
      }
      
    // fetch post data
    // by default, load first page
    get_data(1, "profile", username);

});
