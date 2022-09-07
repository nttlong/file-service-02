import datetime
import struct
from binary_stm import BinaryStream
import re
import utils
from vn_predict.variable_craph import VariableGraph
from vn_predict.yen_top_KShortestPathsAlg import YenTopKShortestPathsAlg


class AccentPredictor:
        def __init__(self):
                self._1Gram = {}
                self._2Grams = {}
                self._1Statistic = {}
                self._accents={}
                self._size1Gram = 216448; #0;
                self._totalCount1Gram = 400508609; #0;
                self._maxWordLength = 8;
                self.maxp = 100;
                self._size2Grams = 5553699; # 0;
                self._totalCount2Grams = 400508022; #0;
                self._globalPosibleChanges:set = set([])
                self._wordsIncorrectPath:str=""
                self.MIN:float = -1000
        def LoadNGGram(self,gram1Path:str,gram2Path:str,statisticPath:str, wordsIncorrectPath:str):
            print("Loading NGrams...")
            print(datetime.datetime.now());
            stopWatch = Stopwatch()
            stopWatch.Start()
            _wordsIncorrectPath = wordsIncorrectPath
            self.load_ng_gram(gram1Path, gram2Path, statisticPath)
            stopWatch.Stop()
            print(f"Time taken: {stopWatch.Elapsed}")
            print("Done!")

        def load_ng_gram(self, gram1Path, gram2Path, statisticPath):
            _accents = self.GetAccentInfo();
            _1Statistic = self.GetNGram1Statistic(statisticPath);
            _1Gram = self.GetNgrams(gram1Path, True);
            _2Grams = self.GetNgrams(gram2Path, True);

        def GetNgrams(self, fileIn,is1Gram:bool)->dict:
            ngrams= {}
            with open(fileIn,'br') as fs:
                reader = BinaryStream(fs)
                count = reader.readInt16()
                for i in range(0,count):
                    ngrams[reader.readString()]=reader.readInt32()

            return ngrams

        def GetNGram1Statistic(self, fileIn)->dict:
            ngrams = {}
            with open(fileIn,"r") as sr:
                line:sr = sr.readline()
                while line!="":
                    indexSpace = line.rindex(' ')
                    indexTab = line.rindex('\t')
                    if indexTab < indexSpace:
                        indexTab = indexSpace
                    ngramWord = line[0: indexTab]
                    ngramCount = int(line.Substring(indexTab + 1))
                    ngrams[ngramWord] = ngramCount
                    line: sr = sr.readline()
            return ngrams

        def GetAccentInfo(self)->set:
            return set([
                "UÙÚỦỤŨƯỪỨỬỰỮ",
                "eèéẻẹẽêềếểệễ",
                "oòóỏọõôồốổộỗơờớởợỡ",
                "OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ",
                "uùúủụũưừứửựữ",
                "DĐ",
                "aàáảạãâầấẩậẫăằắẳặẵ",
                "dđ",
                "AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ",
                "iìíỉịĩ",
                "EÈÉẺẸẼÊỀẾỂỆỄ",
                "YỲÝỶỴỸ",
                "IÌÍỈỊĨ",
                "yỳýỷỵỹ",
            ])

        def GetVocab(self,fileIn):
            output=[]
            with open(fileIn,'w') as fis:
                line:str = fis.readline()
                while line !="":
                    output.append( re.split(line, "\\s+")[0])
                    line: str = fis.readline()

            return set(output)

        def GetGramCount(self,ngramWord:str, ngrams:dict):
            return  ngrams.get(ngramWord,0)
        def SetPosibleChanges(self):
            self._globalPosibleChanges.clear()
            self._globalPosibleChanges=set([])

        def PredictAccentsWithMultiMatches(self,sentence:str, nResults:int, getWeight:bool = True):
            output=dict()
            _in:str = utils.normaliseString(sentence)
            lowercaseIn= _in.lower()
            words=f"{0}{lowercaseIn}{0}".split(' ')
            graph = VariableGraph()
            idxWordMap ={}
            index=0
            numberP =[0]*words.__len__()
            possibleChange =[['']*self.maxp]*words.__len__()
            indices = [[0]*self.maxp]*words.__len__()
            nVertex =0
            index = self.BuildGraph(words, graph, idxWordMap, index, numberP, possibleChange, indices, nVertex)
            yenAlg = YenTopKShortestPathsAlg(graph)
            shortest_paths_list = yenAlg.get_shortest_paths(graph.get_vertex(0), graph.get_vertex(index - 1), nResults)
            for _path in shortest_paths_list:
                pathVertex = _path.get_vertices()
                text = ""
                for i in range(0,pathVertex.Count):
                    vertext = pathVertex[i]
                    text += idxWordMap[vertext.get_id()] + " "
                text = ReplaceWordsIncorrect(text);
                output.Add(ProcessOutput(_in, text.strip()), _path.get_weight());
            if not getWeight:
                return utils.to_string2(output)
            else:
                return utils.to_string(output)


        def BuildGraph(self, words, graph, idxWordMap, index, numberP, possibleChange, indices, nVertex):
            pass









