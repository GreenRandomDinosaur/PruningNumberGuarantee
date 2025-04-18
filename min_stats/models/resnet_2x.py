from __future__ import absolute_import

import math

import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F


__all__ = ['resnet2x']

def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class ResNet2x(nn.Module):

    def __init__(self, depth, num_classes=10):
        super(ResNet2x, self).__init__()
        assert (depth - 2) % 6 == 0, 'depth should be 6n+2'
        n = (depth - 2) // 6
        block = BasicBlock

        self.inplanes = 16*2
        self.conv1 = nn.Conv2d(3, 16*2, kernel_size=3, padding=1,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(16*2)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(block, 16*2, n)
        self.layer2 = self._make_layer(block, 32*2, n, stride=2)
        self.layer3 = self._make_layer(block, 64*2, n, stride=2)
        # self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(64*2, num_classes)

        self.init()
    
    
    def init(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                # nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            # elif isinstance(m,nn.Linear):
                # nn.init.normal_(m.weight, 0, 0.01)
                # nn.init.constant_(m.bias, 0)
    

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)


    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)    

        x = self.layer1(x)  
        x = self.layer2(x)  
        x = self.layer3(x) 

        x = F.avg_pool2d(x,x.size()[3])
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


def resnet2x(**kwargs):
    """
    Constructs a ResNet model.
    """
    return ResNet2x(**kwargs)
