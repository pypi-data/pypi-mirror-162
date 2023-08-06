from string import punctuation
import re

def no_stopwords():

    stopwords = ["alle","andre","arbeid","at","av","bare","begge","ble","blei","bli","blir","blitt",
    "bort","bra","bruke","både","båe","da","de","deg","dei","deim","deira","deires","dem","den",
    "denne","der","dere","deres","det","dette","di","din","disse","ditt","du","dykk","dykkar",
    "då","eg","ein","eit","eitt","eller","elles","en","ene","eneste","enhver","enn","er","et",
    "ett","etter","folk","for","fordi","forsûke","fra","få","før","fûr","fûrst","gjorde",
    "gjûre","god","gå","ha","hadde","han","hans","har","hennar","henne","hennes","her","hjå",
    "ho","hoe","honom","hoss","hossen","hun","hva","hvem","hver","hvilke","hvilken","hvis",
    "hvor","hvordan","hvorfor","i","ikke","ikkje","ingen","ingi","inkje","inn","innen","inni",
    "ja","jeg","kan","kom","korleis","korso","kun","kunne","kva","kvar","kvarhelst","kven",
    "kvi","kvifor","lage","lang","lik","like","makt","man","mange","me","med","medan","meg",
    "meget","mellom","men","mens","mer","mest","mi","min","mine","mitt","mot","mye","mykje",
    "må","måte","navn","ned","nei","no","noe","noen","noka","noko","nokon","nokor","nokre",
    "ny","nå","når","og","også","om","opp","oss","over","part","punkt","på","rett","riktig",
    "samme","sant","seg","selv","si","sia","sidan","siden","sin","sine","sist","sitt","sjøl",
    "skal","skulle","slik","slutt","so","som","somme","somt","start","stille","så","sånn","tid",
    "til","tilbake","tilstand","um","under","upp","ut","uten","var","vart","varte","ved","verdi",
    "vere","verte","vi","vil","ville","vite","vore","vors","vort","vår","være","vært","vöre","vört","å"]

    return stopwords

def tokenizer_one(corpus, min_chars=1):
    '''
    Function to tokenize a text corpus
    '''
    REMOVE_WORDS_MANUALLY = ['endre', 'aug', 'nov', 'mai',
                             'des', 'apr', 'iflg', 'ikr', 'jan', 'juli', 'juni', 'gi',
                             'nr', 'idet', 'jf', 'art', 'gir', 'gis', 'gitt', 'res', 'ta', 'tas',
                             'én', 'år', 'to', 'bør']

    corpus = re.sub(f"[{re.escape(punctuation)}]",
                    "", corpus)  # Remove punctuations
    corpus = re.sub(r"\b[0-9]+\b\s*", "", corpus)  # Remove numbers

    stopwords = no_stopwords()
    tokens = corpus.split()
    clean_tokens = [t for t in tokens if not t in stopwords
                    and len(t) > min_chars
                    and t not in REMOVE_WORDS_MANUALLY]

    return clean_tokens
