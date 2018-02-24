# Akinator clone

REST API and Single Page Application

Uploaded here: refrig.herokuapp.com

Based on algorithm described [here](https://geektimes.ru/post/84364/) and [here](http://www.machinelearning.ru/wiki/images/7/78/BayesML-2010-Yangel-Akinator.pdf).

## REST API

Post an empty object to start playing. You will get game UID and first question:

```
$ echo '{}' | http -b 127.0.0.1:8000/play/
{
    "question": "Is it fruit?", 
    "question_id": 10, 
    "uid": "9277d9aa-7521-4a86-8224-96fe9b4cf0be"
}
```

Then start answering questions:

```
$ http -b 127.0.0.1:8000/play/ uid='9277d9aa-7521-4a86-8224-96fe9b4cf0be' question_id=10 choice='y'
{
    "question": "Is it yellow?", 
    "question_id": 12
}

$ http -b 127.0.0.1:8000/play/ uid='9277d9aa-7521-4a86-8224-96fe9b4cf0be' question_id=12 choice='n'
{
    "question": "Is it red?", 
    "question_id": 11
}

$ http -b 127.0.0.1:8000/play/ uid='9277d9aa-7521-4a86-8224-96fe9b4cf0be' question_id=11 choice='y'
{
    "guess": "Apple", 
    "guess_id": 31
}

$ http -b 127.0.0.1:8000/play/ uid='9277d9aa-7521-4a86-8224-96fe9b4cf0be' guess_id=31 choice='y'
{
    "finish": true
}
```
