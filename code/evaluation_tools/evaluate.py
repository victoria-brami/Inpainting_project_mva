import torch
import numpy as np
from code.evaluation_tools.fid import get_fid
import os
import torchvision

inception_model = torchvision.models.inception_v3(pretrained=False)


class ModelEvaluation:
    def __init__(self, device='cpu'):
        self.device = device
        print("Model Eval initilaized")
        inception_model = torchvision.models.inception_v3(pretrained=False)
        self.model = torch.nn.Sequential(*list(inception_model.children())[:-1])

        print("Inception model loaded")

    def compute_embeddings(self, loader):
        activations = []
        with torch.no_grad():
            for (idx, batch) in enumerate(loader):
                activations.append(self.model(batch))
            activations = torch.cat(activations, dim=0)
        return activations

    @staticmethod
    def compute_activations_statistics(activations):
        activations = activations.cpu().numpy()
        mu = np.mean(activations, axis=0)
        sigma = np.cov(activations, rowvar=False)
        return mu, sigma

    def evaluate_model(self, gt_loader, gen_loader):
        metrics = {}
        gt_features = self.compute_embeddings(gt_loader)
        gen_features = self.compute_embeddings(gen_loader)
        gt_stats = self.compute_activations_statistics(gt_features)
        gen_stats = self.compute_activations_statistics(gen_features)
        gt_params = {"mu": gt_stats[0], "sigma": gt_stats[1]}
        gen_params = {"mu": gen_stats[0], "sigma": gen_stats[1]}

        metrics["fid"] = get_fid(gt_params, gen_params)

        return metrics
