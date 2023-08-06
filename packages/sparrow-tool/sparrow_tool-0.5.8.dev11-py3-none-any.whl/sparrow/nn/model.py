import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

from einops import rearrange, reduce, asnumpy, parse_shape
from einops.layers.torch import Rearrange, Reduce


class TextCNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, n_filters, filter_sizes, output_dim, dropout):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.convs = nn.ModuleList([
            nn.Conv1d(embedding_dim, n_filters, kernel_size=size) for size in filter_sizes
        ])
        self.fc = nn.Linear(len(filter_sizes) * n_filters, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = rearrange(x, 't b -> t b')
        emb = rearrange(self.embedding(x), 't b c -> b c t')
        pooled = [reduce(conv(emb), 'b c t -> b c', 'max') for conv in self.convs]
        concatenated = rearrange(pooled, 'filter b c -> b (filter c)')
        return self.fc(self.dropout(F.relu(concatenated)))


def FastText(vocab_size, embedding_dim, output_dim):
    return nn.Sequential(
        Rearrange('t b -> t b'),
        nn.Embedding(vocab_size, embedding_dim),
        Reduce('t b c -> b c', 'mean'),
        nn.Linear(embedding_dim, output_dim),
        Rearrange('b c -> b c'),
    )


def ConvNet():
    return nn.Sequential(
        nn.Conv2d(1, 10, kernel_size=5),
        nn.MaxPool2d(kernel_size=2),
        nn.ReLU(),
        nn.Conv2d(10, 20, kernel_size=5),
        nn.MaxPool2d(kernel_size=2),
        nn.ReLU(),
        nn.Dropout2d(),
        Rearrange('b c h w -> b (c h w)'),
        nn.Linear(320, 50),
        nn.ReLU(),
        nn.Dropout(),
        nn.Linear(50, 10),
        nn.LogSoftmax(dim=1)
    )


class RNNModel(nn.Module):
    """Container module with an encoder, a recurrent module, and a decoder."""

    def __init__(self, ntoken, ninp, nhid, nlayers, dropout=0.5):
        super().__init__()
        self.drop = nn.Dropout(p=dropout)
        self.encoder = nn.Embedding(ntoken, ninp)
        self.rnn = nn.LSTM(ninp, nhid, nlayers, dropout=dropout)
        self.decoder = nn.Linear(nhid, ntoken)

    def forward(self, input, hidden):
        t, b = input.shape
        emb = self.drop(self.encoder(input))
        output, hidden = self.rnn(emb, hidden)
        output = rearrange(self.drop(output), 't b nhid -> (t b) nhid')
        decoded = rearrange(self.decoder(output), '(t b) token -> t b token', t=t, b=b)
        return decoded, hidden


def channel_shuffle(x, groups):
    return rearrange(x, 'b (c1 c2) h w -> b (c2 c1) h w', c1=groups)


class HighwayConv1d(nn.Conv1d):
    def forward(self, inputs):
        L = super().forward(inputs)
        H1, H2 = rearrange(L, 'b (split c) t -> split b c t', split=2)
        torch.sigmoid_(H1)
        return H1 * H2 + (1.0 - H1) * inputs


class MultiHeadAttentionNew(nn.Module):
    def __init__(self, n_head, d_model, d_k, d_v, dropout=0.1):
        super().__init__()
        self.n_head = n_head

        self.w_qs = nn.Linear(d_model, n_head * d_k)
        self.w_ks = nn.Linear(d_model, n_head * d_k)
        self.w_vs = nn.Linear(d_model, n_head * d_v)

        nn.init.normal_(self.w_qs.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_k)))
        nn.init.normal_(self.w_ks.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_k)))
        nn.init.normal_(self.w_vs.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_v)))

        self.fc = nn.Linear(n_head * d_v, d_model)
        nn.init.xavier_normal_(self.fc.weight)
        self.dropout = nn.Dropout(p=dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, q, k, v, mask=None):
        residual = q
        q = rearrange(self.w_qs(q), 'b l (head k) -> head b l k', head=self.n_head)
        k = rearrange(self.w_ks(k), 'b t (head k) -> head b t k', head=self.n_head)
        v = rearrange(self.w_vs(v), 'b t (head v) -> head b t v', head=self.n_head)
        attn = torch.einsum('hblk,hbtk->hblt', [q, k]) / np.sqrt(q.shape[-1])
        if mask is not None:
            attn = attn.masked_fill(mask[None], -np.inf)
        attn = torch.softmax(attn, dim=3)
        output = torch.einsum('hblt,hbtv->hblv', [attn, v])
        output = rearrange(output, 'head b l v -> b l (head v)')
        output = self.dropout(self.fc(output))
        output = self.layer_norm(output + residual)
        return output, attn


class SequencePrediction(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm1 = nn.LSTMCell(1, 51)
        self.lstm2 = nn.LSTMCell(51, 51)
        self.linear = nn.Linear(51, 1)

    def forward(self, input, future=0):
        b, t = input.shape
        h_t, c_t, h_t2, c_t2 = torch.zeros(4, b, 51, dtype=self.linear.weight.dtype,
                                           device=self.linear.weight.device)

        outputs = []
        for input_t in rearrange(input, 'b t -> t b ()'):
            h_t, c_t = self.lstm1(input_t, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs += [output]

        for i in range(future):  # if we should predict the future
            h_t, c_t = self.lstm1(output, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs += [output]
        return rearrange(outputs, 't b () -> b t')


class SpacialTransform(nn.Module):
    def __init__(self):
        super().__init__()
        # Spatial transformer localization-network
        linear = nn.Linear(32, 3 * 2)
        # Initialize the weights/bias with identity transformation
        linear.weight.data.zero_()
        linear.bias.data.copy_(torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float))

        self.compute_theta = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=7),
            nn.MaxPool2d(2, stride=2),
            nn.ReLU(True),
            nn.Conv2d(8, 10, kernel_size=5),
            nn.MaxPool2d(2, stride=2),
            nn.ReLU(True),
            Rearrange('b c h w -> b (c h w)', h=3, w=3),
            nn.Linear(10 * 3 * 3, 32),
            nn.ReLU(True),
            linear,
            Rearrange('b (row col) -> b row col', row=2, col=3),
        )

    # Spatial transformer network forward function
    def stn(self, x):
        grid = F.affine_grid(self.compute_theta(x), x.size())
        return F.grid_sample(x, grid)


def YOLO_prediction(input, num_classes, num_anchors, anchors, stride_h, stride_w):
    raw_predictions = rearrange(input, 'b (anchor prediction) h w -> prediction b anchor h w',
                                anchor=num_anchors, prediction=5 + num_classes)
    anchors = torch.FloatTensor(anchors).to(input.device)
    anchor_sizes = rearrange(anchors, 'anchor dim -> dim () anchor () ()')

    _, _, _, in_h, in_w = raw_predictions.shape
    grid_h = rearrange(torch.arange(in_h).float(), 'h -> () () h ()').to(input.device)
    grid_w = rearrange(torch.arange(in_w).float(), 'w -> () () () w').to(input.device)

    predicted_bboxes = torch.zeros_like(raw_predictions)
    predicted_bboxes[0] = (raw_predictions[0].sigmoid() + grid_w) * stride_w  # center x
    predicted_bboxes[1] = (raw_predictions[1].sigmoid() + grid_h) * stride_h  # center y
    predicted_bboxes[2:4] = (raw_predictions[2:4].exp()) * anchor_sizes  # bbox width and height
    predicted_bboxes[4] = raw_predictions[4].sigmoid()  # confidence
    predicted_bboxes[5:] = raw_predictions[5:].sigmoid()  # class predictions
    # merging all predicted bboxes for each image
    return rearrange(predicted_bboxes, 'prediction b anchor h w -> b (anchor h w) prediction')
