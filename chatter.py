def train_new_model():
    import os
    os.system('rm -rf model')
    os.system('mkdir -p model')

    from parlai.scripts.train_model import TrainModel
    TrainModel.main(
        # we MUST provide a filename
        model_file='model/model',
        # train on empathetic dialogues
        task='empathetic_dialogues',
        # limit training time to 2 minutes, and a batchsize of 16
        max_train_time=30,
        batchsize=16,
        
        # we specify the model type as seq2seq
        model='seq2seq',
        # some hyperparamter choices. We'll use attention. We could use pretrained
        # embeddings too, with embedding_type='fasttext', but they take a long
        # time to download.
        attention='dot',
        # tie the word embeddings of the encoder/decoder/softmax.
        lookuptable='all',
        # truncate text and labels at 64 tokens, for memory and time savings
        truncate=64,
    )

from parlai.core.teachers import register_teacher, DialogTeacher
@register_teacher("message")
class Messager(DialogTeacher):
    data = None

    def __init__(self, opt, shared=None):
        opt['datafile'] = opt['datatype'].split(':')[0] + ".txt"
        super().__init__(opt, shared)
    
    def setup_data(self, datafile):
        for element in self.data:
            yield element

from parlai.scripts.display_model import RobertDisplayModel

if __name__ == '__main__':
    Messager.data = [[('Hello', 'Hi'), True]]

    ret = RobertDisplayModel.main(
        task='message',
        model_file='model/model',
        verbose=False,
        num_examples=2,
        skip_generation=False,
    )
    print(ret)
