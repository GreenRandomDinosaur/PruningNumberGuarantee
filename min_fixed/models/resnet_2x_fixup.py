import torch
import torch.nn as nn
import numpy as np


__all__ = ['fixup_resnet20_2x', 'fixup_resnet32_2x', 'fixup_resnet56_2x']


def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class FixupBasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(FixupBasicBlock, self).__init__()
        # Both self.conv1 and self.downsample layers downsample the input when stride != 1
        self.bias1a = nn.Parameter(torch.zeros(1))
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bias1b = nn.Parameter(torch.zeros(1))
        self.relu = nn.ReLU(inplace=True)
        self.bias2a = nn.Parameter(torch.zeros(1))
        self.conv2 = conv3x3(planes, planes)
        self.scale = nn.Parameter(torch.ones(1))
        self.bias2b = nn.Parameter(torch.zeros(1))
        self.downsample = downsample

    def forward(self, x):
        identity = x

        out = self.conv1(x + self.bias1a)
        out = self.relu(out + self.bias1b)

        out = self.conv2(out + self.bias2a)
        out = out * self.scale + self.bias2b

        if self.downsample is not None:
            identity = self.downsample(x + self.bias1a)
            identity = torch.cat((identity, torch.zeros_like(identity)), 1)

        out += identity
        out = self.relu(out)

        return out


class FixupResNet(nn.Module):

    def __init__(self, block, layers, num_classes=10):
        super(FixupResNet, self).__init__()
        self.num_layers = sum(layers)
        self.inplanes = 16*2
        self.conv1 = conv3x3(3, 16*2)
        self.bias1 = nn.Parameter(torch.zeros(1))
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(block, 16*2, layers[0])
        self.layer2 = self._make_layer(block, 32*2, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 64*2, layers[2], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.bias2 = nn.Parameter(torch.zeros(1))
        self.fc = nn.Linear(64*2, num_classes)

        
        
        for m in self.modules():
            if isinstance(m, FixupBasicBlock):
                nn.init.normal_(m.conv1.weight, mean=0, std=np.sqrt(2 / (m.conv1.weight.shape[0] * np.prod(m.conv1.weight.shape[2:]))) * self.num_layers ** (-0.5))
                nn.init.normal_(m.conv2.weight, mean=0, std=np.sqrt(2 / (m.conv2.weight.shape[0] * np.prod(m.conv2.weight.shape[2:]))) * self.num_layers ** (-0.5))
                # nn.init.normal_(m.conv1.weight, mean=0, std=np.sqrt(2 / (m.conv1.weight.shape[1] * np.prod(m.conv1.weight.shape[2:]))) * self.num_layers ** (-0.5))
                # nn.init.normal_(m.conv2.weight, mean=0, std=np.sqrt(2 / (m.conv2.weight.shape[1] * np.prod(m.conv2.weight.shape[2:]))) * self.num_layers ** (-0.5))
            # elif isinstance(m, nn.Linear):
                # nn.init.kaiming_normal_(m.weight,mode='fan_out')
                # nn.init.constant_(m.bias, 0)
            # elif isinstance(m, nn.Conv2d):
                # nn.init.kaiming_normal_(m.weight,mode='fan_out')
 
        
        
    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1:
            downsample = nn.AvgPool2d(1, stride=stride)

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes
        for _ in range(1, blocks):
            layers.append(block(planes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x + self.bias1)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x + self.bias2)

        return x


def fixup_resnet20_2x(**kwargs):
    """Constructs a Fixup-ResNet-20 model.
    """
    model = FixupResNet(FixupBasicBlock, [3, 3, 3], **kwargs)
    return model


def fixup_resnet32_2x(**kwargs):
    """Constructs a Fixup-ResNet-32 model.
    """
    model = FixupResNet(FixupBasicBlock, [5, 5, 5], **kwargs)
    return model


def fixup_resnet44_2x(**kwargs):
    """Constructs a Fixup-ResNet-44 model.
    """
    model = FixupResNet(FixupBasicBlock, [7, 7, 7], **kwargs)
    return model


def fixup_resnet56_2x(**kwargs):
    """Constructs a Fixup-ResNet-56 model.
    """
    model = FixupResNet(FixupBasicBlock, [9, 9, 9], **kwargs)
    return model


def fixup_resnet110_2x(**kwargs):
    """Constructs a Fixup-ResNet-110 model.
    """
    model = FixupResNet(FixupBasicBlock, [18, 18, 18], **kwargs)
    return model


def fixup_resnet1202_2x(**kwargs):
    """Constructs a Fixup-ResNet-1202 model.
    """
    model = FixupResNet(FixupBasicBlock, [200, 200, 200], **kwargs)
    return model    