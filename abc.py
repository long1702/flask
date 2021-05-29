import spacy
if __name__ == '__main__':
    nlp = spacy.load('vi_spacy_model')
    doc = nlp('Cộng đồng xử lý ngôn ngữ tự nhiên')
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                token.shape_, token.is_alpha, token.is_stop)