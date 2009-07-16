<html>
<head>
  <script type="text/javascript" src="base.js"></script>
  <script type="text/javascript" src="jscore/base.js"></script>
  <script type="text/javascript" src="jscore/Request.js"></script>
  <script type="text/javascript" src="jscore/Event.js"></script>
  <script type="text/javascript" src="jscore/Loader.js"></script>
  <script type="text/javascript" src="{$pagename}.js"></script>
  {literal}
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
  {/literal}
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
  <span style="font-size: 9px"><a href="whatsnew.html" target="_new">What's New?</a> (4/21/09)</span>
</div>
