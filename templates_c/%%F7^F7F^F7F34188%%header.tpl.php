<?php /* Smarty version 2.6.18, created on 2009-03-22 05:42:23
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
      .statusbox {
        position: absolute;
        left: 300px;
        top: 0px;
        height: 20px;
        width: 200px;
        text-align: center;
        background-color: yellow;
      }
    </style>
  '; ?>

</head>
<body onload="go_go_gadget_loader()">
<div class="statusbox" id="status_box" style="display: none">
Status Box
</div>
<div>
  <span><a href="index.php?p=list">List</a></span>
  <span>&nbsp;</span>
  <span><a href="index.php?p=create">Create</a></span>
  <span>&nbsp;</span>
  <span><a href="index.php?p=manage">Manage My VMs</a></span>
  <span>&nbsp;</span>
  <span style="font-size: 9px"><a href="whatsnew.html" target="_new">What's New?</a> (3/22/09)</span>
</div>