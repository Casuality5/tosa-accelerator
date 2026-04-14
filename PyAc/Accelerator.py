import numpy as np


class Processing:

    def __init__(self, object_patch_vector, task_embedded_vector, weights):
        self.object_patch_vector  = np.array(object_patch_vector)
        self.task_embedded_vector = np.array(task_embedded_vector)
        self.weights = np.array(weights)
        self.size = len(task_embedded_vector)


    
    def PEArray(self):

        ARRAY_OUTPUT = self.object_patch_vector @ self.weights

        return self.ReLU(ARRAY_OUTPUT)
    
    
    def ReLU(self,ARRAY_OUTPUT):

        ReLU_OUTPUT = np.maximum(0, ARRAY_OUTPUT)

        return self.GAP(ReLU_OUTPUT)
    
    def GAP(self,ReLU_OUTPUT):

        VISUAL_EMBEDDING_VECTORS = np.mean(ReLU_OUTPUT, axis = 0)

        return self.SIMILARITY_ENGINE(VISUAL_EMBEDDING_VECTORS)
    
    def SIMILARITY_ENGINE(self,VISUAL_EMBEDDING_VECTORS):

        SIMILARITY_ENGINE_OUTPUT = np.dot(VISUAL_EMBEDDING_VECTORS, self.task_embedded_vector)

        return self.RELEVANCE_SCORE_GENERATOR(SIMILARITY_ENGINE_OUTPUT)
    
    def RELEVANCE_SCORE_GENERATOR(self,SIMILARITY_ENGINE_OUTPUT):

        SCORE = SIMILARITY_ENGINE_OUTPUT

        return SCORE


if __name__ == "__main__":
    
    np.random.seed(0)
    weights = np.random.randn(16, 16)

    patch = np.array([
        [i + j for j in range(16)]
        for i in range(16)
    ], dtype=float) / 10

    task_vector = np.array([
        1, 0.8, 0.6, 0.4,
        0.2, 0, -0.2, -0.4,
        -0.6, -0.8, 1, 0.5,
        0.3, -0.1, 0.7, -0.3
    ])


    print(f"Score:- {Processing(patch, task_vector, weights).PEArray()}")