<?php /* Smarty version 2.6.18, created on 2008-10-26 17:26:36
         compiled from list.tpl */ ?>
<?php $_smarty_tpl_vars = $this->_tpl_vars;
$this->_smarty_include(array('smarty_include_tpl_file' => 'header.tpl', 'smarty_include_vars' => array()));
$this->_tpl_vars = $_smarty_tpl_vars;
unset($_smarty_tpl_vars);
 ?>
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
<?php $_smarty_tpl_vars = $this->_tpl_vars;
$this->_smarty_include(array('smarty_include_tpl_file' => 'footer.tpl', 'smarty_include_vars' => array()));
$this->_tpl_vars = $_smarty_tpl_vars;
unset($_smarty_tpl_vars);
 ?>