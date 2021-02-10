const auth_link = "https://www.strava.com/oauth/token"

function getActivites(res){

    const activities_link = `https://www.strava.com/api/v3/athlete/activities?access_token=${res.access_token}&per_page=200`
    fetch(activities_link)
        .then((res) => console.log(res.json()))
}

function getClubActivites(res){

    const activities_link = `https://www.strava.com/api/v3/athlete/activities?access_token=${res.access_token}&page=5&per_page=10`
    fetch(activities_link)
        .then((res) => console.log(res.json()))

<h2>Make a table based on JSON data.</h2>

<p id="demo"></p>

<script>
var obj, dbParam, xmlhttp, myObj, x, txt = "";
obj = { table: "customers", limit: 20 };
dbParam = JSON.stringify(obj);
xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
    myObj = JSON.parse(this.responseText);
    txt += "<table border='1'>"
    for (x in myObj) {
      txt += "<tr><td>" + myObj[x].name + "</td></tr>";
    }
    txt += "</table>"    
    document.getElementById("demo").innerHTML = txt;
  }
};
xmlhttp.open("POST", "json_demo_html_table.php", true);
xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xmlhttp.send("x=" + dbParam);
</script>

}
function reAuthorize(){
    fetch(auth_link,{
        method: 'post',
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'

        },

        body: JSON.stringify({

            client_id: '58267',
            client_secret: '569b597f7ef7e0717a0478b7e939f86dc4ce0ee7',
            refresh_token: '94cbbccf6d1ad96a4392f3a0d943a093b245526e',
            grant_type: 'refresh_token'
        })
    }).then(res => res.json())
    .then(//res => getActivites(res))
	  res => getClubActivites(res))
      
}

reAuthorize()