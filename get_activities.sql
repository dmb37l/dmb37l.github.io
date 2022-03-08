select  a.id
, 	a.name
,	start_date_local
,	ROUND((distance/1000*0.621371), 2) distance
,	total_elevation_gain
,	ROUND((average_speed/1000*0.621371* 3600), 2) average_speed
,	ROUND((max_speed/1000*0.621371* 3600), 2) max_speed
,	average_cadence
,	average_temp
,	case when device_watts ='true' then average_watts else 0 end average_watts
,	weighted_average_watts
,	kilojoules --round(kilojoules/4.184) calories
--,	device_watts
,	has_heartrate
,	average_heartrate
,	max_heartrate
--,	heartrate_opt_out
,	max_watts
,	moving_time * interval '1 sec' moving_time
,   moving_time mt
,	elapsed_time * interval '1 sec' elapsed_time
,	a.type
--,	timezone
--,	location_country
--,	start_latitude
--,	start_longitude
--,	achievement_count
--,	trainer
--,	commute
--,	manual
--,	private
,	visibility
,	g.name
--,	upload_id_str
,	elev_high
,	elev_low
--,	pr_count
--,	has_kudoed
,	suffer_score
from activities a
left outer join  gear g
on  a.gear_id = g.gear_id
--where start_date_local between '2016-04-17' and '2016-10-17'
--where weighted_average_watts > 0
--and device_watts = 'true'
order by-- case when device_watts ='true' then weighted_average_watts else 0 end  desc 
start_date_local desc


/*select sum (ROUND((distance/1000*0.621371), 2)) distance
from activities a
left outer join  gear g
on  a.gear_id = g.gear_id
--where start_date_local between '2016-04-17' and '2016-10-17'
--where weighted_average_watts > 0
--and device_watts = 'true'
where a.type = 'Ride' 
and start_date_local > '2021-01-01'*/
