CODE_SUCCESS = 0
CODE_FAILED = -1
DUPLICATE = 1

SNAPSHOT_JSON_DATA = """{
                        "id": "root",
                        "topic": "MindMap",
                        "children": [{"id": "easy",
                                      "topic": "Easy",
                                      "direction": "left",
                                      "expanded": false,
                                      "children": [
                                            {"id": "easy1", "topic": "Easy to show"},
                                            {"id": "easy2", "topic": "Easy to edit"},
                                            {"id": "easy3", "topic": "Easy to store"},
                                            {"id": "easy4", "topic": "Easy to embed"}
                                        ]
                                    },
                                    {
                                        "id": "open",
                                        "topic": "Open Source",
                                        "direction": "left",
                                        "expanded": false,
                                        "children": [
                                            {"id": "open1", "topic": "on GitHub"},
                                            {"id": "open2", "topic": "BSD License"}
                                        ]
                                    },
                                    {
                                        "id": "powerful",
                                        "topic": "Powerful",
                                        "direction": "right",
                                        "expanded": false,
                                        "children": [
                                            {"id": "powerful1", "topic": "Base on Javascript"},
                                            {"id": "powerful2", "topic": "Base on HTML5"},
                                            {"id": "powerful3", "topic": "Depends on you"}
                                        ]
                                    },
                                    {
                                        "id": "other",
                                        "topic": "多人协作",
                                        "direction": "right"
                                    }]}"""
