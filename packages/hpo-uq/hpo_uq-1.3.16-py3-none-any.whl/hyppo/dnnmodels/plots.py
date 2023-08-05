# System
import os

# External
import matplotlib.pyplot as plt

def plot_loss(loss,output_name):
    os.makedirs('losses', exist_ok=True)
    plt.style.use('seaborn')
    plt.figure(figsize=(8,5),dpi=200)
    for i in range(loss.shape[1]):
        plt.semilogy(loss[:,i],label='Training' if i==0 else 'Validation')
    plt.grid(True, which="both", ls="-")
    plt.legend(loc='best')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.tight_layout()
    plt.savefig(os.path.join('losses',output_name))
    plt.close()

