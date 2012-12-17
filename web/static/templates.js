window.templates = {
  lobbies: '\
  <div class="card lobby" data-name="{{ name }}" data-password="{{ password }}">\
    <h2>{{ name }}</h2>\
    <h3>by {{ creator }}</h3>\
    <p>{{ players }} / {{ maxplayers }}</p>\
    {{#password}}\
    <img src="/static/lock.png" />\
    {{/password}}\
  </div>',

  user: '\
  <div class="user">\
    <div class="user-name">{{ name }}</div>\
    <div class="user-score">{{ points }}</div>\
  </div>'
}
