# Garden Sensor Log

I built a soil moisture sensor for the raised bed in March and kept this log while it ran.

## Setup

The sensor is a capacitive probe wired to a microcontroller, installed on March 3 in the raised bed by the fence. It reports one reading every ten minutes over the house network, and the readings land in a small SQLite database on the shelf computer. I calibrated it by taking a dry reading in air and a wet reading in a glass of water, and everything in between is a percentage of that range.

## Readings

| Week | Mean moisture | Waterings |
| --- | --- | --- |
| 1 | 41% | 2 |
| 2 | 38% | 3 |
| 3 | 52% | 1 |

The third week was rainy, which is why the mean went up while I watered less.

## Problems

The probe lost its connection twice. The log lines looked like this:

```
# not a heading, just a comment in the log
2026-03-09 14:10 reconnecting to sensor
2026-03-09 14:12 connected
```

Both drops happened on Tuesday afternoons when the microwave was running, so I moved the receiver to the other side of the kitchen.

## Next steps

The next thing I want to do is add a second probe at the far end of the bed, because the readings from one probe only describe one corner of the soil and the far end dries out faster in the afternoon sun. After that I want to log the temperature next to each reading so I can tell whether the moisture swings come from watering or from heat, and then compare a week of readings against the weather station down the road to see how much of the variation is just rain. I also want to move the database off the shelf computer and onto the little file server, since the shelf computer goes to sleep at night and I lose readings between midnight and six in the morning, which is exactly the window I care about for the dew. Once that is stable I will write a small page that shows the last day of readings as a chart so I can check it from my phone without opening a terminal. If the second probe agrees with the first one within a few percent most of the time, I will stop worrying about the sampling question and spend the time on the temperature logging instead, because that is where the interesting variation seems to be. Finally, I want to keep a note of every change I make to the setup, since the first calibration was already hard to reproduce two weeks later when I could not remember which glass of water I had used.
