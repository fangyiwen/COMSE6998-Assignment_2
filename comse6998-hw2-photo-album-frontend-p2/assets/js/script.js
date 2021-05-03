function previewFile() {
  var preview = document.getElementById('image_preview');
  file = document.getElementById('img').files[0]
  var reader = new FileReader();
  reader.addEventListener("load", function () {
    preview.src = reader.result;
  }, false);

  if (file) {
    reader.readAsDataURL(file);
  }
}

function uploadPhotoClick() {
  custom_label = document.getElementById('custom_label').value
  name_label = document.getElementById('name_label').value

  if (custom_label === '' && name_label === '') {
    custom_label = 'name_label'
  } else if (custom_label === '') {
    custom_label = name_label
  } else if (custom_label !== '' && name_label === '') {
    custom_label = custom_label + ', ' + 'name_label'
  } else {
    custom_label = custom_label + ', ' + name_label
  }

  file = document.getElementById('img').files[0]
  filename = file.name

  var reader = new FileReader();
  reader.onloadend = function () {
    var base64result = reader.result.split(',')[1]
    api_gateway_upload(filename, custom_label, base64result)
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

function api_gateway_upload(filename, custom_label, base64result) {
  var params = {
    'x-amz-meta-customLabels': ''
  };

  var body = {
    filename: filename,
    file: base64result
  };

  var additionalParams = {
    headers: {
      'x-amz-meta-customLabels': custom_label
    },
    queryParams: {}
  };

  var apigClient = apigClientFactory.newClient();
  apigClient.uploadPut(params, body, additionalParams)
    .then(function (result) {
      // Add success callback code here.
      console.log('apigClient.uploadPut: success')
      document.getElementById("p1").innerHTML = "<p style='color:green;'>Successful!</p>";
    }).catch(function (result) {
    // Add error callback code here.
    console.log('apigClient.uploadPut: error')
    document.getElementById("p1").innerHTML = "<p style='color:red;'>Error!</p>";
  });
}

function search_by_text() {
  search_query = document.getElementById('input').value

  if (search_query === '') {
    alert("Can't be empty!")
    return;
  }

  var params = {
    'q': search_query
  };

  var body = {};

  var additionalParams = {
    headers: {},
    queryParams: {}
  };

  var apigClient = apigClientFactory.newClient();
  apigClient.searchGet(params, body, additionalParams)
    .then(function (result) {
      // Add success callback code here.
      console.log('apigClient.searchGet: success')
      document.getElementById("p2").innerHTML = "<p style='color:green;'>Successful!</p>";
      show_photo(result.data)
    }).catch(function (result) {
    // Add error callback code here.
    console.log('apigClient.searchGet: error')
    document.getElementById("p2").innerHTML = "<p style='color:red;'>Error!</p>";
  });
}

function show_photo(url_list) {
  document.getElementById('div1').innerHTML = '';
  for (url of url_list) {
    download_photo(url)
  }
}

function download_photo(url) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      base64_encode = xhttp.responseText;
      var img = document.createElement('img');
      img.src = 'data:image/jpeg;base64,' + base64_encode;
      document.getElementById('div1').appendChild(img);
    }
  };
  xhttp.open("GET", url, true);
  xhttp.send();
}
