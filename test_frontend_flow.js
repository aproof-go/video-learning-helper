// 测试前端完整上传流程
const API_BASE_URL = 'http://localhost:8000';

async function testFrontendFlow() {
    console.log('🚀 开始测试前端上传流程...');
    
    try {
        // 1. 登录
        console.log('1️⃣ 登录...');
        const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'upload_test@example.com',
                password: 'test123456'
            })
        });
        
        if (!loginResponse.ok) {
            throw new Error(`登录失败: ${loginResponse.status}`);
        }
        
        const loginData = await loginResponse.json();
        const token = loginData.access_token;
        console.log('✅ 登录成功');
        
        // 2. 上传视频
        console.log('2️⃣ 上传视频...');
        const formData = new FormData();
        // 创建一个简单的测试文件
        const testFile = new Blob(['test video content'], { type: 'video/mp4' });
        formData.append('file', testFile, 'test.mp4');
        formData.append('title', 'Frontend Test Video');
        formData.append('description', 'Test description');
        
        const uploadResponse = await fetch(`${API_BASE_URL}/api/v1/videos/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!uploadResponse.ok) {
            const errorData = await uploadResponse.json().catch(() => ({}));
            throw new Error(`视频上传失败: ${uploadResponse.status} - ${errorData.detail || uploadResponse.statusText}`);
        }
        
        const uploadData = await uploadResponse.json();
        const videoId = uploadData.video_id;
        console.log('✅ 视频上传成功:', videoId);
        
        // 3. 创建分析任务
        console.log('3️⃣ 创建分析任务...');
        const taskData = {
            video_id: videoId,
            video_segmentation: true,
            transition_detection: true,
            audio_transcription: true,
            report_generation: true
        };
        
        console.log('📤 发送的任务数据:', JSON.stringify(taskData, null, 2));
        
        const taskResponse = await fetch(`${API_BASE_URL}/api/v1/analysis/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(taskData)
        });
        
        console.log('📥 任务创建响应状态:', taskResponse.status);
        
        if (!taskResponse.ok) {
            const errorData = await taskResponse.json().catch(() => ({}));
            console.error('❌ 任务创建失败:', {
                status: taskResponse.status,
                statusText: taskResponse.statusText,
                errorData: errorData
            });
            throw new Error(`任务创建失败: ${taskResponse.status} - ${errorData.detail || taskResponse.statusText}`);
        }
        
        const taskResponseData = await taskResponse.json();
        console.log('✅ 分析任务创建成功:', taskResponseData.id);
        
        console.log('🎉 前端流程测试完成！');
        
    } catch (error) {
        console.error('💥 测试失败:', error.message);
        console.error('详细错误:', error);
    }
}

// 运行测试
testFrontendFlow(); 