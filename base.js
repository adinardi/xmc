function set_load_indicator(load) {
  var load_indicator = document.getElementById('load_indicator');
  load_indicator.innerHTML = load;
}

function get_div() {
  return document.createElement('div');
}
