# Language Detection

The usual way to approach this problem in Machine Learning would be to feed the learning algorithm (whatever we chose) with several labeled examples of text in different languages.

Example:

```
"Nosotras nos vamos a tomar nuestro tiempo en escribirlo. No tenemos prisa." <-- Spanish
"Em va fascinar veure l’ingeni subjacent a totes les maniobres." <-- Catalan
"Pay attention whenever you make a mistake, you might be saving someone’s day" <-- English
```

But before jumping into a solution utilizing the power of ML, let's follow the KISS principle (Keep it Simple, Stupid). Why not using a list of 
[stopwords](https://en.wikipedia.org/wiki/Stop_words)?

The solution is really simple:

1. For every language count the number of stop words contained in the text.
2. Select the language that has the max number of ocurrences.

Example:

"___The__ weather __is__ amazing!_" <-- 2 stop words in English ("the","is"), 0 stop words in Spanish. Therefore we say the sentence is in English.  

Jump to code
https://github.com/guiem/metaphor/blob/master/metaphor/utils.py#L10

## First issues
The language detector has been tested on the human rights declaration in different languages sentence by sentence.
Once we get to the numbers we see that the function is only __62%__ accurate. But this is not a big surprise when we print the kind of sentences that make it fail:

"Artículo 24", Spanish

"Article 24", French

"Artikel 24", German

There are no stopwords in such short pieces of text!

Possible solutions:
1. Go for the Machine Learning approach and feed the system with ginormous amounts of labeled text
2. Still avoid ML and store dictionaries (or connect to dictionaries online) and check to what language the words belong to.
3. Keeping it simple! We can make the system require a minimum number of words (or _propper_ sentences) in order to create a metaphor. 

Because the scope of this project is not about language detection, we'll choose number 3 and leave improvement for later ;-)
