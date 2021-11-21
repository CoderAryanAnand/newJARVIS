[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# JARVIS

A new and improved version of the JARVIS I created in 2020
This version works with Tensorflow and NLP. The answers are hardcoded, and will be picked randomly. The questions 
however, will be used to train a model. Check ``training.py`` to see how it trains.

## Usage

If models folder is empty, then run ``training.py`` first, and then run ``chatbot.py``.

## Example

```
> Search iron man on wiki for me please.
Here is what I found on Wikipedia: Iron Man is a superhero appearing in American comic books published by Marvel Comics. The character was co-created by writer and editor Stan Lee, developed by scripter Larry Lieber, and designed by artists Don Heck and Jack Kirby.
See full article here: https://en.wikipedia.org/wiki/Iron_Man
Do you want me to do a google search on this?
> No
Alright
> Bye!
Goodbye!
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Credits
Credit to NeuralNine's YouTube [video](https://youtu.be/1lwddP0KUEg) on ML Chatbots.

He showed me how to make the ``training.py`` and ``chatbot.py``. I added a few arguments after that,
like "type" (see intents.json). I don't completely understand the entire code, but I think
I understand enough.

## License
[MIT](https://choosealicense.com/licenses/mit/)