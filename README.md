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

## License
[MIT](https://choosealicense.com/licenses/mit/)