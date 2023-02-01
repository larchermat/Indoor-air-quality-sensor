# Our Project

## What does it do?

Our project is designed to be implemented in public means of transport such as buses and trains, and it serves to suggest passengers whether to open windows for two main reasons:

1. **Comfort** by means of temperature: sometimes it is better not to turn on air conditioning or heating when we could simply airiate and regulate the indoor temperature thanks to the outdoor temperature
2. **Health conditions** by means of air quality: after a long day of non-stop driving back and forth, the air inside a bus can become pretty heavy due to different pollutants, that we breath in everyday and in the long run may cause serious health problems

## How does it work?

The device is equipped with a sensor (BME680 from Bosch) that can register values such as temperature, humidity and gas resistance, and also takes data of the current weather conditions of the city in which it has been implemented. The program takes in all the data listed above and calculates initially two scores, one based on the indoor and outdoor temperatures plus the weather conditions, and the other based on the data about the humidity and gas resistance; then these two scores are put together in a total score that will show whether it is advisable to airiate or not. The output can be visualized on a screen connected to the device via cloud, but to signal the passenger we use a led stripe that displays a color base on the urgency to open a window:

- `rgb(0,0,255)` : the light will turn blue when there's no urgency; we chose the color blue because it is a soothing color and is related to sanity and health
- `rgb(255,0,255)` : the light will turn violet when the urgency is not yet at max
- `rgb(255,0,0)` : the light will turn red when the need to airiate becomes urgent; we chose the color red because it is associated to danger and is used to alert

## The calculations behind it

The math behind the output is quite simple: the outputs depend on the scores, which are all put on a scale of 0 to 1, with 0 being the worst value and 1 the best.

The temperature score is calculated base on how much the outdoor temperature can improve the indoor: doing some research we figured that the best range for indoor temperatures would be between 20 and 24 degrees Celsius, so we first look if the indoor temperature is inside of that range: if yes we don't do further calcs, if not we look if the outdoor temperature is in the range between the lower or the upper bound and the indoor temperature (if the in temperature is lower then the lower bound we look at the range using the upper bound and vice versa). If yes we calculate the difference between the in and the out temperatures and divide it by the out temperature (which we now take as the optimal temperature), and because of that we get the score. The score is by default set to 1, because we might not calulate it in case of weather conditions that include precipitations.

The indoor air quality score is calculated base on the humidity and gas resistance. After a bit of research we decided that the optimal value for humidity was 40% and for the gas resistance it would be 50kΩ: for the humidity, if the value registered is higher or lower than the optimal, then the score decreases, as for the gas resistance, the score decreases only if the value registered is lower than the optimal value. We calculate individual scores for the humidity and for the gas resistance and put them together giving the both different weights on the result: the humidity makes up 25% of the air quality score and the gas resistance is the 75%.

Once we have calculated the scores for both temperature and air quality we calculate the final score: because we felt that health has priority over comfort, we decided that the score for the air quality would make up 60% of the total score, and temperature 40%. The last thing we do is look in which range the total score falls into: if the score is between 0.75 and 1 it means that there's no urgency, so the color selected for the led is blue; if the score is between 0.5 and 0.75 the light turns violet and if the score falls under 0.5 the led will shine red.

## The code

The code is structured as follows:

- imports
- preparing the sensor: adjustments to the various settings of the sensor; heating the sensor for gas resistance making it run for some time
- setting constants such as the weight of the scores, the optimal values etc...
- main loop of the application:
    - calculate the indoor air quality score and end the humidity value to the adafruit service
    - calculate the temperature score
    - calculate the total score and send it to the adafruit interface
    - give the output signal to the led strip

## The physical part

The physical device is made a box containing the raspberry pi 4, a breadboard and some cables. On the back of the container there's a cut to let out the sensor and on the front we have the led strip
