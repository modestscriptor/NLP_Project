from transformers import RobertaTokenizerFast
from transformers import TFRobertaModel
import tensorflow as tf
from transformers import RobertaTokenizer, RobertaModel
from util import clean_content
import pandas as pd
import numpy as np

def tokenize_roberta(data,tokenizer_roberta,max_len=128) :
    input_ids = []
    attention_masks = []
    for i in range(len(data)):
        encoded = tokenizer_roberta.encode_plus(
            data[i],
            add_special_tokens=True,
            max_length=max_len,
            padding='max_length',
            return_attention_mask=True
            )
        input_ids.append(encoded['input_ids'])
        attention_masks.append(encoded['attention_mask'])
    return np.array(input_ids),np.array(attention_masks)

def roberta_model(bert_model, max_len=128):
    
    opt = tf.keras.optimizers.Adam(learning_rate=1e-5, decay=1e-7)
    loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    accuracy = tf.keras.metrics.BinaryAccuracy()

    input_ids = tf.keras.Input(shape=(max_len,),dtype='int32')
    attention_masks = tf.keras.Input(shape=(max_len,),dtype='int32')
    output = bert_model([input_ids,attention_masks])
    output = output[1]
    output = tf.keras.layers.Dense(128, activation='relu')(output)
    output = tf.keras.layers.Dense(1)(output)
    model = tf.keras.models.Model(inputs = [input_ids,attention_masks],outputs = output)
    model.compile(opt, loss=loss, metrics=accuracy)
    return model


class Sentiment_Model:
    
    def __init__(self,file_path):
        self.tokenizer_roberta = RobertaTokenizerFast.from_pretrained("roberta-base")
        base = TFRobertaModel.from_pretrained('roberta-base')
        model = roberta_model(base)
        model.load_weights(file_path)
        self.model=model

    def score(self,text):
        text=clean_content(text)
        input_id,input_mask=tokenize_roberta(text,self.tokenizer_roberta)
        result_roberta =self.model.predict([input_id,input_mask])
        result_roberta=tf.math.sigmoid(result_roberta)
        result_roberta=tf.reshape(result_roberta,(result_roberta.shape[0],)).numpy()
        return result_roberta