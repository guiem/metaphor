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
https://github.com/guiem/metaphor/blob/master/metaphor/utils.py#L7
