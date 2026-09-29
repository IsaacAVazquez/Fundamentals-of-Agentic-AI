from personal_wiki.textutil import content_terms, split_sentences, stem, tokenize


def test_tokenize_keeps_decimals_and_alnum():
    assert tokenize("lr 0.0001 on the M4 Pro") == ["lr", "0.0001", "on", "the", "m4", "pro"]
    assert tokenize("Pac-Man E4B") == ["pac", "man", "e4b"]


def test_stem():
    assert stem("trained") == stem("training") == stem("trains") == "train"
    assert stem("games") == "game"
    assert stem("is") == "is"
    assert stem("0.0001") == "0.0001"
    assert stem("matches") == "match"


def test_content_terms_drops_stopwords():
    assert content_terms("What did I use for the DQN?") == ["use", "dqn"]
    assert content_terms("the and of") == []


def test_split_sentences():
    assert split_sentences("One thing. Another thing! A third? Done.") == ["One thing.", "Another thing!", "A third?", "Done."]
