document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  

  // submit form
  document.querySelector('#compose-form').onsubmit = function() {
    
    // form data
    let formData = {
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    };

    // sent to Django API
    fetch('emails', {
      method: 'post',
      body: JSON.stringify(formData)
    })
    .then(response => {
      if (response.ok){
        return response.json();
      } else {
        throw new Error(response.status);
      }
    })  
    .then(json => {
      console.log(json);
      load_mailbox('sent');
    })
    .catch(error => console.log(error));

    // do not submit the form
    return false;
  };

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // create grid structure for email info and archive button
  const sub_email_view = document.createElement('div');
  sub_email_view.setAttribute('id', 'sub-emails-view');
  document.querySelector('#emails-view').appendChild(sub_email_view);


  const div_email_info = document.createElement('div');
  const div_archive_btn = document.createElement('div');
  div_email_info.setAttribute('class', 'div_email_info');
  div_archive_btn.setAttribute('class', 'div_archive_btn');


  sub_email_view.appendChild(div_email_info);
  sub_email_view.appendChild(div_archive_btn);



  // get data
  fetch(`emails/${mailbox}`)
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(response.status);
    }
  })
  .then(json => {
    //console.log(json);
    json.forEach(ele => {

      let email_div = document.createElement('div');
      email_div.setAttribute('class', 'email_div');

      if(ele.read){
        email_div.style.backgroundColor = 'grey';
      }

      let emailData = `<p class="ptag"><span class="sender">${ele.sender}</span> ${ele.subject} <span class="timestamp">${ele.timestamp}</span></p>`;
      email_div.innerHTML = emailData;
      email_div.addEventListener('click', function() {
        // mark email as read
        if(!ele.read) {
          mark_as_read(ele.id);
        }
        // show email
        show_email(ele.id);
      });

      div_email_info.append(email_div);
      
      // append archive button
      if(mailbox != 'sent') {
        let btn_div = document.createElement('div');
        btn_div.setAttribute('class', 'btn_div');
        
        let archive_btn = document.createElement('button');
        archive_btn.setAttribute('class', 'btn btn-sm btn-outline-primary');
        if(ele.archived) {
          archive_btn.innerText = "Unarchive";
        } else {
          archive_btn.innerText = "Archive";
        }
        
        archive_btn.addEventListener('click', () => {
          archive(ele.id, mailbox);
        });

        btn_div.append(archive_btn);
        div_archive_btn.append(btn_div);
      }

    });
  })
  .catch(error => console.log(error));
  
}

function mark_as_read(mail_id) {
  let requestOptions = {
    method: 'put',
    body: JSON.stringify({
      read: true
    })
  };

  fetch(`emails/${mail_id}`, requestOptions)
  .then(response => {
    if (!response.ok) {
      throw new Error(response.status);
    }
  })
  .catch(error => console.log(error));

}

function show_email(email_id){
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email').style.display = 'block';

  const email_div = document.querySelector('#email');
  email_div.innerHTML = '';

  fetch(`emails/${email_id}`)
  .then(response => {
    if (response.ok) {
      return response.json()
    } else {
      throw new Error(response.status);
    }
  })
  .then(json => {
    // show email
    let emailData = document.createElement('div');
    let emailBody = document.createElement('div');
    emailData.setAttribute('class', 'email-data');
    emailBody.setAttribute('class', 'email-body');

    let from_ = `<p><span>From:</span> ${json.sender}</p>`;
    let to_ = '';
    json.recipients.forEach(recipient => {
      to_ += `${recipient}, `;
    });
    to_ = '<p><span>To:</span> ' + to_.slice(0, -2) + '</p>' // remove last two char from to list (', ')
    let subject_ = `<p><span>Subject:</span> ${json.subject}</p>`;
    let timestamp_ = `<p><span>Timestamp:</span> ${json.timestamp}</p>`;
    let replybutton = '<button class="btn btn-sm btn-outline-primary" id="reply-button">Reply</button>'
    let body_ = json.body;

    emailData.innerHTML = '<hr>' + from_ + to_ + subject_ + timestamp_ + replybutton + '<hr>';
    emailBody.innerHTML = body_.replace(/\n/g, '<br>');

    email_div.append(emailData);
    email_div.append(emailBody);

    document.querySelector('#reply-button').addEventListener('click', () => {
      compose_email();
      // Fill composition fields with email data
      document.querySelector('#compose-recipients').value = json.sender;
      document.querySelector('#compose-subject').value = json.subject.slice(0,3) === 'Re:' ? json.subject : 'Re: ' + json.subject;
      let emailBody = `\n\nOn ${json.timestamp} ${json.sender} wrote: \n${json.body}`
      document.querySelector('#compose-body').value = emailBody;
    });
  })
  .catch(error => console.log(error))

}

function archive(mail_id, mailbox){
  let requestOptions = {
    method: 'put',
    body: JSON.stringify({
      archived: ele.archived ? false : true
    })
  };

  fetch(`emails/${mail_id}`, requestOptions)
  .then(response => {
    if (!response.ok) {
      throw new Error(response.status);
    } else {
      load_mailbox('inbox'); // maybe is better to load the current mailbox using 'mailbox'
    }
  })
  .catch(error => console.log(error));

}
