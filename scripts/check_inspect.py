#!/usr/bin/env python3
"""Optional installed-Inspect integration check; never starts Docker or a model."""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspect_ai.model import ModelOutput, get_model
from inspect_ai.scorer import Target
from inspect_ai.solver import TaskState
from ctf.bench27.recent2026_eval import recent2026, exact_flag
from ctf.ctf_eval import ctf, ctf_pico, ctf_deep
from inspect_cyber import create_agentic_eval_dataset
from inspect_evals.cybench.cybench import CHALLENGES_DIR
from unittest.mock import patch


async def main():
    # Construct the gateway client without sending a request or using real keys.
    with patch('socket.socket.connect', side_effect=AssertionError('Network access during offline check')):
        get_model('openai-api/offline/model', api_key='offline-placeholder', base_url='http://127.0.0.1:9/v1')
    cybench = create_agentic_eval_dataset(root_dir=CHALLENGES_DIR.absolute())
    selected = cybench.filter_by_metadata_field('eval_name',
        ['slcg', 'missingbits', 'back_to_the_past', 'glacier_exchange', 'network_tools',
         'permuted', 'delulu', 'just_another_pickle_jail']).filter_by_metadata_field('variant_name', 'hard')
    assert len(selected) == 8, 'Expected eight upstream Cybench tasks'
    task = recent2026()
    assert len(task.dataset) == 12
    for sample in task.dataset:
        for file in sample.files.values():
            assert Path(file).is_file(), file
    assert len(ctf().dataset) > 0
    assert len(ctf_pico().dataset) > 0
    assert len(ctf_deep().dataset) == 3
    score = exact_flag()
    for answer, expected in [('lactf{ok}', 'C'), ('lactf{bad} lactf{ok}', 'I'), ('lactf{оk}', 'I')]:
        state = TaskState(model='mockllm/model', sample_id='offline', epoch=1,
                          input='offline', messages=[], output=ModelOutput.from_content('mockllm/model', answer))
        result = await score(state, Target('lactf{ok}'))
        assert result.value == expected, (answer, result)
    print('PASS: gateway SDK, eight Cybench tasks, custom/archive loaders and flag scorer; no API/Docker calls')


if __name__ == '__main__':
    asyncio.run(main())
