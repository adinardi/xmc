{include file='header.tpl'}
Manage VMs (<a href="#" onclick="load_vm_list({ldelim}all:1{rdelim});">all</a>)
<style>
  .vmbox {ldelim}
    float: left;
    width: 100;
    height: 100;
    border: 2px solid blue;
  {rdelim}
  .vmon {ldelim}
    border-color: green;
  {rdelim}
  .vmoff {ldelim}
    border-color: red;
  {rdelim}
</style>
<div id="vmcontainer">

</div>
{include file='footer.tpl'}
