window.templates =
  lobbies:
    '{{ #lobbies }}
    <div class="lobbies">
      <div class="card lobby btn" data-index="{{ index }}">
        {{ name }}<br />
        {{ players }}/{{ maxplayers }}<br />
    </div>
    {{ /lobbies }}'
