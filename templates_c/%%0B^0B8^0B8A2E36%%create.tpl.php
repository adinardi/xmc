<?php /* Smarty version 2.6.18, created on 2008-12-09 09:44:15
         compiled from create.tpl */ ?>
<?php $_smarty_tpl_vars = $this->_tpl_vars;
$this->_smarty_include(array('smarty_include_tpl_file' => 'header.tpl', 'smarty_include_vars' => array()));
$this->_tpl_vars = $_smarty_tpl_vars;
unset($_smarty_tpl_vars);
 ?>
VM Create <span id="load_indicator"></span>
<div>Hello <span id="username">Loading...</span></div>
<br>
<div>You have <span id="avail_vms">Loading...</span> pre-allocated VM available: (click row to use)</div>
<style>
  .vmtable {
    border-collapse: collapse;
  }
  .vmtable td, th {
    padding-left: 5px;
    padding-right: 5px;
  }
  .vmtable tr {
    background-color: lightgrey;
    border: 2px solid white;
  }
</style>

<div style="border: 1px solid blue; display: inline-block; padding: 1px;">
<table id="allocvms" style="" class="vmtable">
  <thead>
    <th>Disk</th>
    <th>Swap</th>
    <th>Mem</th>
    <th>MAC</th>
  </thead>
  <tbody id="allocvms_tbody">
  </tbody>
</table>
</div>

<br><br>
<div id="vmconfigStatus"></div>
<div id="vmconfig" style="display: none">
<b>VM Properties</b>
<table style="border: 1px solid black">
  <tr>
    <td>Hostname:</td>
    <td><input type="text" id="hname">.csh.rit.edu&nbsp;<span id="hname_avail" style="font-weight: bold">-</span></td>
  </tr>
  <tr>
    <td>Memory (M):</td>
    <td><input type="text" id="mem"></td>
  </tr>
  <tr>
    <td>Disk Size (M):</td>
    <td><input type="text" id="dsize" value=""></td>
  </tr>
  <tr>
    <td>Swap Size (M):</td>
    <td><input type="text" id="ssize" value=""></td>
  </tr>
  <tr>
    <td>Base Image:</td>
    <td><select id="imagename"></select></td>
  </tr>
  <tr>
    <td>Mac Address (00:16:3e:xx:xx:xx):</td>
    <td><input type="text" id="mac_address"><br>
      <input type="checkbox" id="start_register" checked="checked" value="on"><label for="start_register">Register automatically on start</label></td>
  </tr>
  <tr>
    <td>Owner:</td>
    <td><input type="text" id="owner"></td>
  </tr>
  <tr>
    <td colspan=2><button onclick="go_create_vm()">Create</button></td>
  <td>
</table>
</div>

<?php $_smarty_tpl_vars = $this->_tpl_vars;
$this->_smarty_include(array('smarty_include_tpl_file' => 'footer.tpl', 'smarty_include_vars' => array()));
$this->_tpl_vars = $_smarty_tpl_vars;
unset($_smarty_tpl_vars);
 ?>