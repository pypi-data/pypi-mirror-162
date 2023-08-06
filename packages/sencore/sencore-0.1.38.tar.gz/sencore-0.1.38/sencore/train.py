import json
import csv
from sencore import VocabParser, PhraseParser
import click


def _write_to_csv(fields, content, csvfile="review.csv"):
  #print('Create {} file'.format(csvfile))
  with open(csvfile, encoding="utf8", mode='w') as output_file:
    dict_writer = csv.DictWriter(output_file, restval="-", fieldnames=fields, delimiter='\t')
    dict_writer.writeheader()
    dict_writer.writerows(content)

@click.command()
@click.option("--lang", help="Specify the language", default="en", prompt="Language")
@click.option("--senfile", help="Specify the sentence file in json", prompt="Sentence file")
@click.option("--dstname", help="Specify the phrase review file", prompt="Review file")
def generate_review_phrases(lang, senfile, dstname):
  pp = PhraseParser(lang)

  with open(senfile, encoding="utf8") as f:
    TEXTS = json.loads(f.read())

  np_content = []
  v_content = []

  for sen in TEXTS:
    phrases = pp.digest(sen)

    np_content.append({"sentence": sen, "phrases": json.dumps(phrases["noun_phrases"])})
    v_content.append({"sentence": sen, "verbs": json.dumps(phrases["verbs"])})

  _write_to_csv(["sentence", "phrases"], np_content, csvfile=dstname+".noun_phrase.csv")
  _write_to_csv(["sentence", "verbs"], v_content, csvfile=dstname+".verb.csv")



