import numpy as np
from collections import defaultdict
import random
from .utils import get_neighbors, get_move_direction
from constants import MOVE_COSTS

class QLearning:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        # Khởi tạo các tham số
        self.learning_rate = learning_rate  # Tốc độ học
        self.discount_factor = discount_factor  # Hệ số chiết khấu
        self.exploration_rate = exploration_rate  # Tỷ lệ khám phá
        self.q_table = defaultdict(lambda: defaultdict(float))  # Bảng Q
        self.min_exploration_rate = 0.01  # Tỷ lệ khám phá tối thiểu
        self.exploration_decay = 0.995  # Tốc độ giảm tỷ lệ khám phá

    def get_state_key(self, state):
        # Chuyển đổi trạng thái thành khóa có thể băm được
        return tuple(map(tuple, state))

    def get_action(self, state, possible_actions):
        # Chọn hành động theo chiến lược epsilon-greedy
        if random.random() < self.exploration_rate:
            # Khám phá: chọn ngẫu nhiên
            return random.choice(possible_actions)
        else:
            # Khai thác: chọn hành động có giá trị Q cao nhất
            state_key = self.get_state_key(state)
            q_values = [self.q_table[state_key][action] for action in possible_actions]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(possible_actions, q_values) if q == max_q]
            return random.choice(best_actions)

    def update_q_value(self, state, action, reward, next_state, next_possible_actions):
        # Cập nhật giá trị Q
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Tính giá trị Q tối đa cho trạng thái tiếp theo
        next_q_values = [self.q_table[next_state_key][next_action] for next_action in next_possible_actions]
        max_next_q = max(next_q_values) if next_q_values else 0
        
        # Cập nhật giá trị Q theo công thức Q-learning
        current_q = self.q_table[state_key][action]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q

    def calculate_reward(self, state, next_state, goal_state):
        # Tính phần thưởng dựa trên khoảng cách đến mục tiêu
        from .informed import heuristic
        current_h = heuristic(state, goal_state)
        next_h = heuristic(next_state, goal_state)
        
        # Phần thưởng cơ bản
        reward = -1  # Phạt cho mỗi bước đi
        
        # Thưởng nếu tiến gần hơn đến mục tiêu
        if next_h < current_h:
            reward += 2
        
        # Thưởng lớn nếu đạt được mục tiêu
        if next_state == goal_state:
            reward += 100
            
        return reward

    def train(self, env, num_episodes):
        # Huấn luyện agent
        best_reward = float('-inf')
        best_path = None
        
        for episode in range(num_episodes):
            state = env.reset()
            done = False
            total_reward = 0
            path = [state]
            
            while not done:
                # Lấy các hành động có thể thực hiện
                possible_actions = env.get_possible_actions()
                
                # Chọn hành động
                action = self.get_action(state, possible_actions)
                
                # Thực hiện hành động
                next_state, reward, done = env.step(action)
                
                # Tính toán phần thưởng
                reward = self.calculate_reward(state, next_state, env.goal_state)
                
                # Cập nhật giá trị Q
                next_possible_actions = env.get_possible_actions()
                self.update_q_value(state, action, reward, next_state, next_possible_actions)
                
                state = next_state
                path.append(state)
                total_reward += reward
            
            # Cập nhật tỷ lệ khám phá
            self.exploration_rate = max(self.min_exploration_rate, 
                                     self.exploration_rate * self.exploration_decay)
            
            # Lưu lại đường đi tốt nhất
            if total_reward > best_reward:
                best_reward = total_reward
                best_path = path
            
            # In thông tin về episode
            if (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}, Exploration Rate: {self.exploration_rate:.3f}")
        
        return best_path

    def get_best_action(self, state, possible_actions):
        # Lấy hành động tốt nhất cho trạng thái hiện tại
        state_key = self.get_state_key(state)
        q_values = [self.q_table[state_key][action] for action in possible_actions]
        max_q = max(q_values)
        best_actions = [action for action, q in zip(possible_actions, q_values) if q == max_q]
        return random.choice(best_actions)    