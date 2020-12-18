const auth_link = "https://www.strava.com/oauth/token"

function getActivites(res){

    const activities_link = `https://www.strava.com/api/v3/athlete/activities?access_token=${res.access_token}`
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

            client_id: '58448',
            client_secret: '424db41c1cb7e8718fbbcf17192e7bb0e3fe5a91',
            refresh_token: 'ea9f23435419a1c02159a8fb8cba8377c87c8c3e',
            grant_type: 'refresh_token'
        })
    })
    .then(res => getActivites(res))
      
}

reAuthorize()