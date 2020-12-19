const auth_link = "https://www.strava.com/oauth/token"

function getActivites(res){

    const activities_link = `https://www.strava.com/api/v3/athlete/activities?access_token=f162a4534571cb0a9efa3fb17cc7514718d49749` //--${res.access_token}'
    fetch(activities_link)
        .then((res) => console.log(res.json()))
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
    })
    .then(res => getActivites(res))
      
}

reAuthorize()