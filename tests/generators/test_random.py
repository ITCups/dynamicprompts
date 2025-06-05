from collections import Counter
from unittest.mock import patch

import pytest
from dynamicprompts.generators.randomprompt import RandomPromptGenerator
from dynamicprompts.wildcards import WildcardManager

from tests.samplers.utils import patch_random_sampler_wildcard_choice
from tests.conftest import (
    sampling_context_lazy_fixtures,
)

@pytest.fixture
def generator(wildcard_manager: WildcardManager) -> RandomPromptGenerator:
    return RandomPromptGenerator(wildcard_manager)


class TestRandomGenerator:
    def test_literal_template(self, generator):
        prompt = "I love bread"

        prompts = list(generator.generate(prompt, 10))

        assert len(prompts) == 10
        assert prompts[0] == prompt

    def test_generate_with_wildcard(self, generator):
        prompt = "I saw a __animals/mammals/*__"  # refers to a real wildcard
        animals = ["dog", "dog", "wolf", "tiger"]  # ... but we'll mock it

        with patch_random_sampler_wildcard_choice(animals):
            prompts = list(generator.generate(prompt, 4))

        assert [str(p) for p in prompts] == [f"I saw a {animal}" for animal in animals]

    def test_without_wildcard_manager(self):
        generator = RandomPromptGenerator()
        assert generator._context.wildcard_manager.path is None

    def test_generate_with_seeds_wrong_length(self, generator: RandomPromptGenerator):
        with pytest.raises(ValueError) as exc_info:
            generator.generate(num_images=3, seeds=[42, 44])
        assert str(exc_info.value) == "Expected 3 seeds, but got 2"

    def test_generate_with_template_and_seeds(self, generator: RandomPromptGenerator):
        with patch.object(generator._context.rand, "seed", autospec=True) as mock_seed:
            generator.generate(template="test_template", num_images=2, seeds=[42, 43])

            mock_seed.assert_any_call(42)
            mock_seed.assert_any_call(43)

    def test_generate_with_one_seed(self, generator: RandomPromptGenerator):
        with patch.object(generator._context.rand, "seed", autospec=True) as mock_seed:
            generator.generate(template="test_template", num_images=2, seeds=[42])

            mock_seed.assert_any_call(42)
            assert mock_seed.call_count == 2
            assert mock_seed.call_args_list[0] == mock_seed.call_args_list[1]

    def test_generate_with_int_seed(self, generator: RandomPromptGenerator):
        with patch.object(generator._context.rand, "seed", autospec=True) as mock_seed:
            generator.generate(template="test_template", num_images=2, seeds=42)

            mock_seed.assert_any_call(42)
            assert mock_seed.call_count == 2
            assert mock_seed.call_args_list[0] == mock_seed.call_args_list[1]

    def test_cyclical_sampler_with_seeds(self, generator: RandomPromptGenerator):
        template = "A {@red|green|blue} ball"
        prompts = generator.generate(template=template, num_images=3, seeds=[1, 2, 3])
        assert [str(p) for p in prompts] == [
            "A red ball",
            "A green ball",
            "A blue ball",
        ]

    def test_weighted_wildcard(self, generator: RandomPromptGenerator):
        prompt = "I saw a __weighted-animals/heavy__"
        prompts = Counter(generator.generate(prompt, 1500))
        # Over 1500 generations with a non-biased RNG we should always the correct order...
        assert [s for s, n in prompts.most_common()] == [
            "I saw a elephant",
            "I saw a rhino",
            "I saw a hippo",
            "I saw a giraffe",
        ]

    # including seeds with following tests to get predictable results for assertion
    def test_probability_basic(self, generator: RandomPromptGenerator):
        s = """{0.5::beach}"""
        prompts = generator.generate(s, 10, seeds=['1','2','3','4','5','6','7','8','9','10'])
        assert prompts == ['beach', '', '', 'beach', 'beach', 'beach', '', 'beach', 'beach', '']

    def test_probability_negative_test_variant(self, generator: RandomPromptGenerator):
        s = """{0.5::beach|pool}"""
        prompts = generator.generate(s, 10, seeds=['5','1','457','2','5','85','151','8','523','10'])
        assert prompts != ['beach', '', '', 'beach', 'beach', 'beach', '', 'beach', 'beach', '']
        
    def test_probability_zero_chance(self, generator: RandomPromptGenerator):
        s = """{0.0::beach }"""
        prompts = generator.generate(s, 10, seeds=['1','2','3','4','5','6','7','8','9','10'])
        assert prompts == ['', '', '', '', '', '', '', '', '', '']
        s = """{0::beach}"""
        prompts = generator.generate(s, 10, seeds=['1','2','3','4','5','6','7','8','9','10'])
        assert prompts == ['', '', '', '', '', '', '', '', '', '']
        
    def test_probability_solid_chance(self, generator: RandomPromptGenerator):
        s = """{1.0::beach}"""
        prompts = generator.generate(s, 10, seeds=['1','2','3','4','5','6','7','8','9','10'])
        assert prompts == ['beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach']
        s = """{1::beach}"""
        prompts = generator.generate(s, 10, seeds=['1','2','3','4','5','6','7','8','9','10'])
        assert prompts == ['beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach', 'beach']
        
    def test_probability_basic_nested(self, generator: RandomPromptGenerator):
        s = """{0.5::{beach|pool}}"""
        prompts = generator.generate(s, 10, seeds=['124','12345','16223','1232541','2151','1241251','4363','8164','9423','241'])
        assert prompts == ['', 'beach', '', '', 'pool', '', '', 'pool', '', '']

    def test_condition_basic_1(self, generator: RandomPromptGenerator):
        s = """fire {fire::ball}"""
        prompts = generator.generate(s)
        assert prompts == ["fire ball"]

    def test_condition_basic_2(self, generator: RandomPromptGenerator):
        s = """fire, {fire::ball}"""
        prompts = generator.generate(s)
        assert prompts == ["fire, ball"]


    def test_condition_basic_3(self, generator: RandomPromptGenerator):
        s = """,fire{fire::ball}"""
        prompts = generator.generate(s)
        assert prompts == [",fireball"]

    def test_condition_basic_4(self, generator: RandomPromptGenerator):
        s = """{water|fire}{fire::ball}{water::bolt}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['waterbolt', 'fireball', 'fireball', 'fireball', 'waterbolt']
        
    def test_condition_basic_5(self, generator: RandomPromptGenerator):
        s = """{water {bucket |ball {red|orange}}|fire} {fire::strike} {water::bolt} {bucket::wooden} {ball::round} {red::soviet} {orange::tasty}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['water bucket   bolt wooden   ', 'fire strike     ', 'fire strike     ', 'fire strike     ', 'water ball orange  bolt  round  tasty']
        
    def test_condition_basic_6(self, generator: RandomPromptGenerator):
        s = """{bucket|ball} {water|fire} {red|orange} {fire::strike} {water::bolt} {bucket::wooden} {ball::round} {red::soviet} {orange::tasty}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['bucket water red  bolt wooden  soviet ',
                           'ball water red  bolt  round soviet ',
                           'ball water red  bolt  round soviet ',
                           'ball fire orange strike   round  tasty',
                           'bucket fire orange strike  wooden   tasty']

    def test_condition_basic_8(self, generator: RandomPromptGenerator):
        s = r"""fire{fire::{blast|bolt|strike}} {(?!.*fireplace.*)fire.*\s::hit} {(?!.*shield.*)(?!.*person.*)hit::a wall}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['firebolt hit a wall', 'firestrike hit a wall', 'firebolt hit a wall', 'firebolt hit a wall', 'fireblast hit a wall']
        
    def test_condition_basic_9(self, generator: RandomPromptGenerator):
        s = r"""metal, {\b(?!(?:egg)\b)\w+::boiling}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['metal, boiling', 'metal, boiling', 'metal, boiling', 'metal, boiling', 'metal, boiling']


    def test_condition_basic_if_else_1(self, generator: RandomPromptGenerator):
        s = """fire{fire::ball|bolt}"""
        prompts = generator.generate(s)
        assert prompts == ["fireball"] 

    def test_condition_basic_if_else_2(self, generator: RandomPromptGenerator):
        s = """water{fire::ball|bolt}"""
        prompts = generator.generate(s)
        assert prompts == ['waterbolt']

    def test_condition_basic_if_else_3(self, generator: RandomPromptGenerator):
        s = """water{fire::|bolt}"""
        prompts = generator.generate(s)
        assert prompts == ['waterbolt']

    def test_condition_chance_wildcard(self, generator: RandomPromptGenerator):
        s = """__condition_chance_test/chance__ __condition_chance_test/condition__"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['water  bolt ', '   ', '   ', ' fire  ball', 'water  bolt ']

    def test_condition_basic_nested_1(self, generator: RandomPromptGenerator):
        s = r"""fire{fire::{blast|bolt|strike}} {(?!.*fireplace.*)fire.*\s::hit} {magical shield:: that is deflected by the shield} {(?!.*fireplace.*)(?!.*magical shield.*)person::, person is on fire} {fireplace::, person is resting} {(?!.*shield.*)(?!.*person.*)hit:: a wall}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['firebolt hit    a wall', 'firestrike hit    a wall', 'firebolt hit    a wall', 'firebolt hit    a wall', 'fireblast hit    a wall']

    def test_condition_basic_nested_2(self, generator: RandomPromptGenerator):
        s = r"""person, magical shield, fire{fire::{blast|bolt|strike}} {(?!.*fireplace.*)fire.*\s::hit} {magical shield:: that is deflected by the shield} {(?!.*fireplace.*)(?!.*magical shield.*)person::, person is on fire} {fireplace::, person is resting} {(?!.*shield.*)(?!.*person.*)hit:: a wall}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['person, magical shield, firebolt hit that is deflected by the shield   ', 'person, magical shield, firestrike hit that is deflected by the shield   ', 'person, magical shield, firebolt hit that is deflected by the shield   ', 'person, magical shield, firebolt hit that is deflected by the shield   ', 'person, magical shield, fireblast hit that is deflected by the shield   ']

    def test_condition_basic_nested_3(self, generator: RandomPromptGenerator):
        s = r"""person, fire{fire::{blast|bolt|strike}} {(?!.*fireplace.*)fire.*\s::hit} {magical shield:: that is deflected by the shield} {(?!.*fireplace.*)(?!.*magical shield.*)person::, person is on fire} {fireplace::, person is resting} {(?!.*shield.*)(?!.*person.*)hit:: a wall}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['person, firebolt hit  , person is on fire  ', 'person, firestrike hit  , person is on fire  ', 'person, firebolt hit  , person is on fire  ', 'person, firebolt hit  , person is on fire  ', 'person, fireblast hit  , person is on fire  ']
        
    def test_condition_basic_nested_4(self, generator: RandomPromptGenerator):
        s = r"""person, fireplace{fire::{blast|bolt|strike}} {(?!.*fireplace.*)fire.*\s::hit} {magical shield:: that is deflected by the shield} {(?!.*fireplace.*)(?!.*magical shield.*)person::, person is on fire} {fireplace::, person is resting} {(?!.*shield.*)(?!.*person.*)hit:: a wall}"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['person, fireplacebolt    , person is resting ', 'person, fireplacestrike    , person is resting ', 'person, fireplacebolt    , person is resting ', 'person, fireplacebolt    , person is resting ', 'person, fireplaceblast    , person is resting ']

    def test_condition_basic_nested_5(self, generator: RandomPromptGenerator):
        s = r"""fire,
                {
                    {(water|fire|air)::
                        {elemental|spell|rune}
                    }
                }"""
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['fire,\n                spell\n                    \n                ',
                           'fire,\n                rune\n                    \n                ',
                           'fire,\n                spell\n                    \n                ',
                           'fire,\n                spell\n                    \n                ',
                           'fire,\n                elemental\n                    \n                ']

    def test_condition_basic_wildcard(self, generator: RandomPromptGenerator):
        s = ("""__condition_chance_test/chance__ __condition_chance_test/condition__""")
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['water  bolt ', '   ', '   ', ' fire  ball', 'water  bolt ']


    def test_condition_negative_1(self, generator: RandomPromptGenerator):
        s = """fire{water::ball}"""
        prompts = generator.generate(s)
        assert prompts == ["fire"]

    def test_condition_negative_2(self, generator: RandomPromptGenerator):
        s = """{fire::ball}fire"""
        prompts = generator.generate(s)
        assert prompts == ["fire"]

    def test_condition_negative_3(self, generator: RandomPromptGenerator):
        s = """fireplace{fire\\s::ball}"""
        prompts = generator.generate(s)
        assert prompts == ["fireplace"]
        
    def test_condition_negative_4(self, generator: RandomPromptGenerator):
        # should be a variant
        s = ("""{(water:1.2) (fire:1.6)| (earth:1.8) {0.08::air}| 0.15::(wild:1.8) {0.3::(magic:1.8)}}""")
        prompts = generator.generate(s, 5, seeds=['1','2','3','4','5'])
        assert prompts == ['(earth:1.8) ', '(earth:1.8) ', '(earth:1.8) ', '(earth:1.8) ', '(water:1.2) (fire:1.6)']
        
    def test_condition_basic_comments_1(self, generator: RandomPromptGenerator):
        s = r"""{*fire?*}{fire\?::hot!}"""
        prompts = generator.generate(s)
        assert prompts == ['hot!']
    def test_condition_basic_comments_2(self, generator: RandomPromptGenerator):
        s = r"""{*cinders and fire?*}{fire\?::hot!}"""
        prompts = generator.generate(s)
        assert prompts == ['hot!']
        
    def test_condition_basic_test_comment_basic_1(self, generator: RandomPromptGenerator):
        s = """{*comment*}"""
        prompts = generator.generate(s)
        assert prompts == ['']
