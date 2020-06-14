import math

class ChunkGenerator:
    def __init__(self):
        self.data_per_chunk = 200
        self.responses_per_chunk = 5
        self.max_num_chunks = 5

    def generate_data_chunks(self, data):
        return self.generate_chunks(data, self.data_per_chunk)

    def generate_response_chunks(self, responses):
        return self.generate_chunks(responses, self.responses_per_chunk)

    def generate_chunks(self, data, data_per_chunk):
        data_size = len(data)
        num_chunks = int(math.floor(data_size / data_per_chunk))

        if num_chunks > 0:
            data_chunks = [data[i::num_chunks] for i in range(num_chunks)]
        elif num_chunks > self.max_num_chunks:
            num_chunks = self.max_num_chunks
            data_chunks = [data[i::num_chunks] for i in range(num_chunks)]

        else:
            num_chunks = 1
            data_chunks = [data[i::num_chunks] for i in range(num_chunks)]


        return data_chunks, num_chunks