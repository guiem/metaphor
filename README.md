# Metaphor

[![Coverage Status](https://coveralls.io/repos/github/guiem/metaphor/badge.svg?branch=master)](https://coveralls.io/github/guiem/metaphor?branch=master)

Artificial Intelligence system to create metaphors.

I :heart: literature & writing. I am also an Artificial Intelligence nerd. So I thought: "Y U NOT BUILT AUTOMATIC METAPHOR SYSTEM?" :trollface:

Here you'll find an attempt to build a text beautifier that's able to create new analogies. 

## How?

Well, the main idea behind it consists of using [Word embeddings](https://en.wikipedia.org/wiki/Word_embedding). 

I will explore other strategies, but the first approach I want to try contemplates `word2vec` because I think it's a very powerful tool to deal with language semantics (I believe it can be applied to other domains, **spam detection**, **profile matching**, etc.).

### How is it different from simply using synonyms?

I know, you could say "OMG, so far your approach is really simple. Basically you only replace words with other similar words."

But it is waaay cooler than that, for starters nobody has given the machine any specific `map` function between words and its synonyms.

Everything the machine learns is based on the **[Distributional Hypothesis](https://en.wikipedia.org/wiki/Distributional_semantics#Distributional_Hypothesis)**, which states that words that appear in the same contexts share semantic meaning.

I'm afraid there is a pile of mathematical technicalities behind `word2vec`, but for the sake of a simple intuition you can imagine it works based on this assumption:

* If `P(w | a) = P(w | b)` it means that words `a` and `b` somehow share a context.

Same statement with a simple example:

* If the probability of observing the word `pet` given that we've seen the word `cat` equals the probability of observing the word `pet` given we've seen the word `dog` we can assume that both `cat` and `dog` share some sort of meaning. 

Sure, in real life we won’t get an exact equality, just words being close to each other. Words close in this space are often synonyms (e.g. happy and delighted), antonyms (e.g. good and evil) or other easily interchangeable words (e.g. yellow and blue).


Check the [Metaphor's wiki](https://github.com/guiem/metaphor/wiki) and learn more!