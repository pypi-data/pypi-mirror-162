DisFlood - library for flood to discord channel on library discontrol
Flooding to channel 
Special Keys:
```python
!rand! # library replacing this to random number 0 to 10000
``` 
Using this library:
```python
from DisFlood.DisFlood import DisFlood
from discontrol.Client import Client
from discontrol.Message import Message
cli = Client('Your Super Puper Secret Token')
disflode = DisFlood(cli)
disflode.SetChannel(789988291864035328) #channelid
disflode.SetCountMessages(60) # count messages for send
disflode.SetCountMessagesForInterval(5) # messages for interval
disflode.SetInterval(3) # interval on flout
try:
    disflode.Flood("Hello, !rand! people ! ")
except:
    pass
```
packages for this library:
```python
pip install requests
```
```python
pip install discontrol
```
Have fun to flood friends !
