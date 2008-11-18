{include file='header.tpl'}
{literal}
<style>
  body {
    -moz-user-select: none;
  }
</style>
{/literal}
VM List <a href="#" onclick="go_go_load_data()">Refresh</a><span id="load_indicator"></span>
<table id="vmlist">
  <thead>
    <tr>
      <th>PM</th>
      <th>VM</th>
      <th>Mem</th>
    </tr>
  </thead>
  <tbody id="vmlist-body">
  </tbody>
</table>
<div id="container">

</div>
{include file='footer.tpl'}
