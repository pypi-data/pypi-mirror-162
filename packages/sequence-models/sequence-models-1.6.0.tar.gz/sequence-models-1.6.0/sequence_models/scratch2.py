from sequence_models.pretrained import load_model_and_alphabet
from sequence_models.constants import PROTEIN_ALPHABET

import torch

model, collater = load_model_and_alphabet('carp_640M')

seqs = [['ASDFTR'], ['ASDFTR-']]
x = collater(seqs)[0]
rep = model(x, result='logits')
sm = torch.nn.Softmax(dim=2)
prob = sm(rep)
idx = torch.argmax(prob, dim=2)
prob[0][torch.arange(7), x[0]]
x.shape
[PROTEIN_ALPHABET[i] for i in idx[0]]

seqs = [['MDREQ'], ['MGTRRLLP']]
x.shape
rep = model(x)