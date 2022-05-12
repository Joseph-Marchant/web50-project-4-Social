document.addEventListener('DOMContentLoaded', function() {
    var edits = document.getElementsByClassName('edit');
    var saves = document.getElementsByClassName('save');
    for (var i=0; i<edits.length; i++) {
        edits[i].style.display = 'block';
        saves[i].style.display = 'none';
    };
})

function edit_post(post_id) {

    // Get the div containing the content
    const post = document.getElementById('post_' + post_id);

    // Change the class to edit 
    post.classList.remove('post-content');
    post.classList.add('edit-post-content');
    post.disabled=false;

    // Hide edit and show save button
    const edit = document.getElementById('edit_' + post_id);
    const save = document.getElementById('save_' + post_id);
    edit.style.display = 'none';
    save.style.display = 'block';
}

function save_edit(post_id) {

    // Get the updated post
    const post = document.getElementById('post_' + post_id);

    // Turn off edit
    post.classList.remove('edit-post-content');
    post.classList.add('post-content');
    post.disabled=true;

    // Show edit and hide save button
    const edit = document.getElementById('edit_' + post_id);
    const save = document.getElementById('save_' + post_id);
    edit.style.display = 'block';
    save.style.display = 'none';

    // Send the data to be update
    fetch('/edit', {
        method: 'POST',
        body: JSON.stringify({
            content: post.value,
            id: post_id
        })
    })

    // Get the response
    .then(response => response.json())
    .then(result => {
        console.log(result);
    });
}

function like(post_id) {

    // Update the like class
    const like = document.getElementById('like_' + post_id);
    console.log(like)
    like.classList.add('liked');
    var count = like.innerHTML;
    count = count.slice(0, -6)
    count = parseInt(count) + 1
    like.innerHTML = `${count} Likes`

    // Change the function clicking like will perform
    like.setAttribute('onclick', `unlike(${post_id})`)

    // Send to server for updating
    fetch('/like', {
        method: 'POST',
        body: JSON.stringify({
            post_id: post_id
        })
    })

    // Get the response
    .then(response => response.json())
    .then(result => {
        console.log(result);
    });
}

function unlike(post_id) {
    // Update the like class
    const like = document.getElementById('like_' + post_id);
    like.classList.remove('liked');
    var count = like.innerHTML;
    count = count.slice(0, -6)
    count = parseInt(count) - 1
    like.innerHTML = `${count} Likes`

    // Change the function clicking like will perform
    like.setAttribute('onclick', `like(${post_id})`)

    // Send to server for updating
    fetch('/unlike', {
        method: 'POST',
        body: JSON.stringify({
            post_id: post_id
        })
    })

    // Get the response
    .then(response => response.json())
    .then(result => {
        console.log(result);
    });
}