<?
require_once('smarty/Smarty.class.php');

$smarty = new Smarty();

$smarty->template_dir = 'templates/';
$smarty->compile_dir = 'templates_c';
$smarty->config_dir = 'configs/';
$smarty->cache_dir = 'cache/';

//$smarty->debugging = true;
require_once($_GET['p'] . ".inc");
$smarty->assign('pagename', $_GET['p']);
$smarty->display($_GET['p'] . '.tpl');
?>
