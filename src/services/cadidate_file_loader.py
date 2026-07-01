import json
import gzip


class CandidateFileLoader:

    @staticmethod
    def load(uploaded_file):

        name = uploaded_file.name.lower()

        if name.endswith(".json"):

            return json.load(uploaded_file)

        if name.endswith(".jsonl"):

            return [
                json.loads(line)
                for line in uploaded_file
                .read()
                .decode("utf-8")
                .splitlines()
                if line.strip()
            ]

        if name.endswith(".jsonl.gz"):

            contents = uploaded_file.read()

            text = gzip.decompress(
                contents
            ).decode("utf-8")

            return [
                json.loads(line)
                for line in text.splitlines()
                if line.strip()
            ]

        raise ValueError(
            "Unsupported candidate file"
        )