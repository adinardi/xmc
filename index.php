<?
require_once('smarty/Smarty.class.php');

$smarty = new Smarty();

$smarty->template_dir = 'templates/';
$smarty->compile_dir = 'templates_c';
$smarty->config_dir = 'configs/';
$smarty->cache_dir = 'cache/';

//$smarty->debugging = true;
$page = $_GET['p'];
if (strlen($page) == 0) {
  $page = 'manage';
}
require_once($page . ".inc");
$smarty->assign('pagename', $page);
$smarty->display($page . '.tpl');
?>
