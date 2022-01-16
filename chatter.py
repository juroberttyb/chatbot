def train_new_model():
    import os
    os.system('rm -rf new_model')
    os.system('mkdir -p new_model')

    from parlai.scripts.train_model import TrainModel
    """
    TrainModel.main(
        # we MUST provide a filename
        model_file='new_model/model',
        # train on empathetic dialogues
        task='empathetic_dialogues',
        # limit training time to 2 minutes, and a batchsize of 16
        max_train_time=120,
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
    """

    """
    TrainModel.main(
        # similar to before
        task='empathetic_dialogues', 
        model='transformer/generator',
        model_file='new_model/model',
        
        # initialize with a pretrained model
        # init_model='zoo:tutorial_transformer_generator/model',
        
        # arguments we get from the pretrained model.
        # Unfortunately, these must be looked up separately for each model.
        n_heads=8, n_layers=8, n_positions=512, text_truncate=512,
        label_truncate=128, ffn_size=2048, embedding_size=256,
        activation='gelu', variant='xlm',
        dict_lower=True, dict_tokenizer='bpe',
        dict_file='zoo:tutorial_transformer_generator/model.dict',
        learn_positional_embeddings=True,
        
        # some training arguments, specific to this fine-tuning
        # use a small learning rate with ADAM optimizer
        lr=1e-5, optimizer='adam',
        warmup_updates=100,
        # early stopping on perplexity
        validation_metric='ppl',
        # train at most x seconds, and validate every 0.25 epochs
        max_train_time=6*60*60, validation_every_n_epochs=1.0,
        
        # depend on your gpu. If you have a V100, this is good
        batchsize=12, fp16=True, fp16_impl='mem_efficient',
        
        # speeds up validation
        skip_generation=True,
        
        # helps us cram more examples into our gpu at a time
        dynamic_batching='full',
    )
    """

    TrainModel.main(
        # similar to before
        task='empathetic_dialogues', 
        model='transformer/generator',
        model_file='new_model/model',
        
        # initialize with a pretrained model
        init_model='zoo:tutorial_transformer_generator/model',
        
        # arguments we get from the pretrained model.
        # Unfortunately, these must be looked up separately for each model.
        n_heads=16, n_layers=8, n_positions=512, text_truncate=512,
        label_truncate=128, ffn_size=2048, embedding_size=512,
        activation='gelu', variant='xlm',
        dict_lower=True, dict_tokenizer='bpe',
        dict_file='zoo:tutorial_transformer_generator/model.dict',
        learn_positional_embeddings=True,
        
        # some training arguments, specific to this fine-tuning
        # use a small learning rate with ADAM optimizer
        lr=1e-5, optimizer='adam',
        warmup_updates=100,
        # early stopping on perplexity
        validation_metric='ppl',
        # train at most 10 minutes, and validate every 0.25 epochs
        max_train_time=60, validation_every_n_epochs=0.25,
        
        # depend on your gpu. If you have a V100, this is good
        batchsize=10, fp16=True, fp16_impl='mem_efficient',
        
        # speeds up validation
        skip_generation=True,
        
        # helps us cram more examples into our gpu at a time
        dynamic_batching='full',
    )

    os.system('rm -rf model')
    os.system("mv new_model model")
    os.system('rm -rf new_model')

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
    train_new_model()

    """
    Messager.data = [[['how'], True], [['yes'], False], [['no'], False], [['oh'], False], [['taler'], False]]

    ret = RobertDisplayModel.main(
        task='message',
        model_file='model/model',
        verbose=False,
        num_examples=5,
        skip_generation=False,
    )
    print(ret)
    print(len(ret))
    """
