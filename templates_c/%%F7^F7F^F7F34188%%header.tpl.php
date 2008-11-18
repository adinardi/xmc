<?php /* Smarty version 2.6.18, created on 2008-11-17 05:49:23
         compiled from header.tpl */ ?>
<html>
<head>
  <script type="text/javascript" src="base.js"></script>
  <script type="text/javascript" src="jscore/base.js"></script>
  <script type="text/javascript" src="jscore/Request.js"></script>
  <script type="text/javascript" src="jscore/Event.js"></script>
  <script type="text/javascript" src="jscore/Loader.js"></script>
  <script type="text/javascript" src="<?php echo $this->_tpl_vars['pagename']; ?>
.js"></script>
  <?php echo '
    <style>
      body, table {
        font-family: Arial;
        font-size: 14px;
      }
      a {
        color: blue;
      }
    </style>
  '; ?>

</head>
<body onload="go_go_gadget_loader()">
<div>
  <span><a href="index.php?p=list">List</a></span>
  <span>&nbsp;</span>
  <span><a href="index.php?p=create">Create</a></span>
  <span>&nbsp;</span>
  <span><a href="index.php?p=manage">Manage My VMs</a></span>
</div>