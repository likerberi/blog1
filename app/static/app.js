// 화면 요소 참조
const outputEl = document.getElementById("output");
const idEl = document.getElementById("item-id");
const titleEl = document.getElementById("item-title");
const descriptionEl = document.getElementById("item-description");
const doneEl = document.getElementById("item-done");
const codeFlowEl = document.getElementById("code-flow");

// [Step 3] 인증 요소 (나중에 로드되므로 함수로 접근)
const getAuthUsername = () => document.getElementById("auth-username");
const getAuthPassword = () => document.getElementById("auth-password");
const getTokenStatus = () => document.getElementById("token-status");

// [Step 3] 저장된 토큰
let accessToken = null;

// ============================================================
// 코드 흐름 표시 (학습용)
// ============================================================
const codeFlows = {
  // Step 1: 메모리 버전
  health: `
    <div class="flow-step">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes.py</div>
        <span class="keyword">@router</span>.<span class="function">get</span>(<span class="string">"/health"</span>)<br>
        <span class="keyword">def</span> <span class="function">health_check</span>():<br>
        &nbsp;&nbsp;<span class="keyword">return</span> {<span class="string">"status"</span>: <span class="string">"ok"</span>}
      </div>
    </div>
    <p class="hint">가장 단순한 엔드포인트 - 서비스/저장소 없이 바로 응답</p>
  `,
  create: `
    <div class="flow-step">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes.py (라우터)</div>
        <span class="keyword">@router</span>.<span class="function">post</span>(<span class="string">"/items"</span>)<br>
        <span class="keyword">def</span> <span class="function">create_item</span>(payload: <span class="highlight">ItemCreate</span>):<br>
        &nbsp;&nbsp;<span class="comment"># Pydantic이 자동으로 title, description 검증</span><br>
        &nbsp;&nbsp;<span class="keyword">return</span> service.<span class="function">create_item</span>(payload)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num">2</span>
      <div class="code-block">
        <div class="file-name">app/services.py (서비스)</div>
        <span class="keyword">def</span> <span class="function">create_item</span>(self, payload):<br>
        &nbsp;&nbsp;self.<span class="function">_ensure_title_unique</span>(payload.title) <span class="comment"># 중복 체크</span><br>
        &nbsp;&nbsp;<span class="keyword">return</span> self._repository.<span class="function">create_item</span>(...)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num">3</span>
      <div class="code-block">
        <div class="file-name">app/repository.py (저장소)</div>
        <span class="keyword">def</span> <span class="function">create_item</span>(self, title, description):<br>
        &nbsp;&nbsp;item = Item(...)<br>
        &nbsp;&nbsp;self._items[item.id] = item <span class="comment"># dict에 저장</span><br>
        &nbsp;&nbsp;<span class="keyword">return</span> item
      </div>
    </div>
  `,
  list: `
    <div class="flow-step">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes.py → services.py → repository.py</div>
        라우터 → 서비스 → 저장소 순서로 호출<br>
        <span class="keyword">return</span> list(self._items.<span class="function">values</span>()) <span class="comment"># 메모리에서 조회</span>
      </div>
    </div>
  `,

  // Step 2: DB 버전 (의존성 주입 강조)
  health_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_db.py</div>
        <span class="keyword">@router</span>.<span class="function">get</span>(<span class="string">"/health"</span>)<br>
        <span class="keyword">def</span> <span class="function">health_check</span>():<br>
        &nbsp;&nbsp;<span class="keyword">return</span> {<span class="string">"status"</span>: <span class="string">"ok"</span>, <span class="string">"storage"</span>: <span class="string">"sqlite"</span>}
      </div>
    </div>
  `,
  create_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_db.py (의존성 주입!)</div>
        <span class="keyword">@router</span>.<span class="function">post</span>(<span class="string">"/items"</span>)<br>
        <span class="keyword">def</span> <span class="function">create_item</span>(<br>
        &nbsp;&nbsp;payload: ItemCreate,<br>
        &nbsp;&nbsp;service: ItemDBService = <span class="highlight">Depends(get_item_service)</span><br>
        ):<br>
        <span class="comment"># ↑ Depends가 자동으로 서비스 인스턴스를 만들어서 주입!</span>
      </div>
    </div>
    <div class="flow-step db">
      <span class="step-num">2</span>
      <div class="code-block">
        <div class="file-name">app/database.py (세션 생성)</div>
        <span class="keyword">def</span> <span class="function">get_db</span>():<br>
        &nbsp;&nbsp;db = SessionLocal()<br>
        &nbsp;&nbsp;<span class="keyword">try</span>:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="highlight">yield db</span> <span class="comment"># 세션을 "빌려줌"</span><br>
        &nbsp;&nbsp;<span class="keyword">finally</span>:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;db.<span class="function">close</span>() <span class="comment"># 요청 끝나면 자동 정리</span>
      </div>
    </div>
    <div class="flow-step db">
      <span class="step-num">3</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py (DB 저장)</div>
        <span class="keyword">def</span> <span class="function">create_item</span>(self, title, description):<br>
        &nbsp;&nbsp;self._db.<span class="function">add</span>(item)<br>
        &nbsp;&nbsp;self._db.<span class="function">commit</span>() <span class="comment"># DB에 저장!</span><br>
        &nbsp;&nbsp;self._db.<span class="function">refresh</span>(item)
      </div>
    </div>
  `,
  list_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">의존성 주입 체인</div>
        <span class="highlight">Depends(get_db)</span> → DB 세션 생성<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span class="highlight">Depends(get_item_service)</span> → 서비스에 세션 주입<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        라우터 함수 실행<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        요청 완료 → <span class="function">db.close()</span> 자동 호출
      </div>
    </div>
    <div class="flow-step db">
      <span class="step-num">2</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        <span class="keyword">return</span> self._db.<span class="function">query</span>(ItemModel).<span class="function">all</span>() <span class="comment"># SQLAlchemy 쿼리</span>
      </div>
    </div>
  `,
  get_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        <span class="keyword">return</span> self._db.<span class="function">query</span>(ItemModel).<span class="function">filter</span>(ItemModel.id == item_id).<span class="function">first</span>()
      </div>
    </div>
  `,
  update_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        item.title = title<br>
        self._db.<span class="function">commit</span>() <span class="comment"># 변경사항 저장</span><br>
        self._db.<span class="function">refresh</span>(item) <span class="comment"># DB에서 다시 읽기</span>
      </div>
    </div>
  `,
  delete_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        self._db.<span class="function">delete</span>(item)<br>
        self._db.<span class="function">commit</span>()
      </div>
    </div>
  `,
  reset_db: `
    <div class="flow-step db">
      <span class="step-num">1</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        self._db.<span class="function">query</span>(ItemModel).<span class="function">delete</span>()<br>
        self._db.<span class="function">commit</span>()
      </div>
    </div>
  `,

  // Step 3: 인증 버전
  register: `
    <div class="flow-step" style="--step-color: #dc2626;">
      <span class="step-num" style="background: #dc2626;">1</span>
      <div class="code-block">
        <div class="file-name">app/auth.py (비밀번호 해싱)</div>
        <span class="keyword">def</span> <span class="function">create_user</span>(username, password):<br>
        &nbsp;&nbsp;hashed = <span class="highlight">get_password_hash(password)</span> <span class="comment"># bcrypt 해싱</span><br>
        &nbsp;&nbsp;user = {<span class="string">"username"</span>: username, <span class="string">"hashed_password"</span>: hashed}<br>
        &nbsp;&nbsp;fake_users_db[username] = user
      </div>
    </div>
    <p class="hint">비밀번호는 절대 평문으로 저장하지 않음!</p>
  `,
  login: `
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_auth.py (로그인)</div>
        <span class="keyword">@router</span>.<span class="function">post</span>(<span class="string">"/login"</span>)<br>
        <span class="keyword">def</span> <span class="function">login</span>(form_data: <span class="highlight">OAuth2PasswordRequestForm</span> = Depends()):<br>
        <span class="comment"># OAuth2 표준 폼으로 username/password 받음</span>
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">2</span>
      <div class="code-block">
        <div class="file-name">app/auth.py (비밀번호 검증)</div>
        <span class="keyword">def</span> <span class="function">authenticate_user</span>(username, password):<br>
        &nbsp;&nbsp;user = get_user(username)<br>
        &nbsp;&nbsp;<span class="keyword">if</span> <span class="highlight">verify_password(password, user["hashed_password"])</span>:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword">return</span> user
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">3</span>
      <div class="code-block">
        <div class="file-name">app/auth.py (JWT 토큰 생성)</div>
        <span class="keyword">def</span> <span class="function">create_access_token</span>(data, expires_delta):<br>
        &nbsp;&nbsp;to_encode = {<span class="string">"sub"</span>: username, <span class="string">"exp"</span>: expire_time}<br>
        &nbsp;&nbsp;<span class="keyword">return</span> <span class="highlight">jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")</span>
      </div>
    </div>
    <p class="hint">로그인 성공 → JWT 토큰 발급 → 클라이언트가 저장</p>
  `,
  me: `
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">1</span>
      <div class="code-block">
        <div class="file-name">요청 헤더</div>
        Authorization: <span class="highlight">Bearer eyJhbGciOiJIUzI1NiIs...</span>
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">2</span>
      <div class="code-block">
        <div class="file-name">app/auth.py (토큰 검증)</div>
        <span class="keyword">async def</span> <span class="function">get_current_user</span>(token = <span class="highlight">Depends(oauth2_scheme)</span>):<br>
        &nbsp;&nbsp;payload = <span class="highlight">jwt.decode(token, SECRET_KEY)</span><br>
        &nbsp;&nbsp;username = payload.get(<span class="string">"sub"</span>)<br>
        &nbsp;&nbsp;<span class="keyword">return</span> get_user(username)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">3</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_auth.py</div>
        <span class="keyword">@router</span>.<span class="function">get</span>(<span class="string">"/me"</span>)<br>
        <span class="keyword">def</span> <span class="function">read_users_me</span>(current_user = <span class="highlight">Depends(get_current_active_user)</span>):<br>
        &nbsp;&nbsp;<span class="comment"># current_user는 자동으로 인증된 사용자 정보!</span><br>
        &nbsp;&nbsp;<span class="keyword">return</span> current_user
      </div>
    </div>
    <p class="hint">Depends 체인: oauth2_scheme → get_current_user → get_current_active_user</p>
  `,
  list_auth: `
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_auth.py (보호된 엔드포인트)</div>
        <span class="keyword">@router</span>.<span class="function">get</span>(<span class="string">"/protected/items"</span>)<br>
        <span class="keyword">def</span> <span class="function">list_items_protected</span>(<br>
        &nbsp;&nbsp;service = Depends(get_item_service),<br>
        &nbsp;&nbsp;current_user = <span class="highlight">Depends(get_current_active_user)</span> <span class="comment"># 인증 필수!</span><br>
        ):<br>
        &nbsp;&nbsp;<span class="keyword">return</span> service.list_items()
      </div>
    </div>
    <p class="hint">current_user 파라미터가 있으면 자동으로 인증 체크!</p>
  `,
  create_auth: `
    <div class="flow-step">
      <span class="step-num" style="background: #dc2626;">1</span>
      <div class="code-block">
        <div class="file-name">의존성 주입 체인</div>
        <span class="highlight">Depends(get_db)</span> → DB 세션<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span class="highlight">Depends(get_item_service)</span> → 서비스<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span class="highlight">Depends(get_current_active_user)</span> → 인증된 사용자<br>
        &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        라우터 함수 실행
      </div>
    </div>
    <p class="hint">여러 Depends를 동시에 사용 가능!</p>
  `,

  // Step 4: 비동기 + 백그라운드
  async_list: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_async.py</div>
        <span class="highlight">async def</span> <span class="function">list_items_async</span>(...):<br>
        &nbsp;&nbsp;<span class="keyword">return</span> <span class="highlight">await</span> service.list_items_async()
      </div>
    </div>
    <p class="hint">async def + await = 비동기 함수. I/O 대기 중 다른 요청 처리 가능!</p>
  `,
  async_create: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_async.py</div>
        <span class="highlight">async def</span> <span class="function">create_item_async</span>(<br>
        &nbsp;&nbsp;payload: ItemCreate,<br>
        &nbsp;&nbsp;<span class="highlight">background_tasks: BackgroundTasks</span>, <span class="comment"># 주입!</span><br>
        ):<br>
        &nbsp;&nbsp;item = <span class="highlight">await</span> service.create_item_async(payload)<br>
        &nbsp;&nbsp;<span class="comment"># 여기서 응답 반환 (사용자는 여기까지만 대기)</span><br>
        &nbsp;&nbsp;background_tasks.<span class="function">add_task</span>(후처리함수, ...)<br>
        &nbsp;&nbsp;<span class="keyword">return</span> item
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">2</span>
      <div class="code-block">
        <div class="file-name">응답 후 백그라운드 실행</div>
        로그 기록 → 검색 인덱스 → 캐시 갱신 → 알림 발송<br>
        <span class="comment"># 사용자는 이미 응답 받음!</span>
      </div>
    </div>
  `,
  sequential: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">순차 처리 (느림)</div>
        result1 = <span class="highlight">await</span> api_call(1) <span class="comment"># 0.5초 대기</span><br>
        result2 = <span class="highlight">await</span> api_call(2) <span class="comment"># 0.5초 대기</span><br>
        result3 = <span class="highlight">await</span> api_call(3) <span class="comment"># 0.5초 대기</span><br>
        <span class="comment"># 총 1.5초!</span>
      </div>
    </div>
    <p class="hint">하나 끝나면 다음 시작 → 총 시간 = 합계</p>
  `,
  concurrent: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">동시 처리 (빠름!)</div>
        results = <span class="highlight">await asyncio.gather</span>(<br>
        &nbsp;&nbsp;api_call(1), <span class="comment"># 동시 시작</span><br>
        &nbsp;&nbsp;api_call(2), <span class="comment"># 동시 시작</span><br>
        &nbsp;&nbsp;api_call(3), <span class="comment"># 동시 시작</span><br>
        )<br>
        <span class="comment"># 총 0.5초! (가장 느린 것 기준)</span>
      </div>
    </div>
    <p class="hint">모두 동시에 시작 → 총 시간 ≈ 가장 느린 작업 시간</p>
  `,
  bg_log: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_async.py</div>
        background_tasks.<span class="function">add_task</span>(<span class="highlight">write_log</span>, message)<br>
        <span class="keyword">return</span> {<span class="string">"status"</span>: <span class="string">"accepted"</span>}<br>
        <span class="comment"># 응답 즉시 반환!</span>
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">2</span>
      <div class="code-block">
        <div class="file-name">app/background.py (응답 후 실행)</div>
        <span class="keyword">def</span> <span class="function">write_log</span>(message):<br>
        &nbsp;&nbsp;time.sleep(0.5) <span class="comment"># 파일 I/O</span><br>
        &nbsp;&nbsp;<span class="keyword">with</span> open(<span class="string">"log.txt"</span>, <span class="string">"a"</span>) <span class="keyword">as</span> f:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;f.write(message)
      </div>
    </div>
  `,
  bg_email: `
    <div class="flow-step">
      <span class="step-num" style="background: #7c3aed;">1</span>
      <div class="code-block">
        <div class="file-name">백그라운드 이메일</div>
        background_tasks.<span class="function">add_task</span>(<br>
        &nbsp;&nbsp;<span class="highlight">send_email_notification</span>,<br>
        &nbsp;&nbsp;email, subject, body<br>
        )<br>
        <span class="keyword">return</span> {<span class="string">"status"</span>: <span class="string">"accepted"</span>}
      </div>
    </div>
    <p class="hint">이메일 발송은 2~5초 걸리지만 사용자는 즉시 응답!</p>
  `,

  // Step 5: 에러 핸들링 코드 흐름
  test_duplicate: `
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">1</span>
      <div class="code-block">
        <div class="file-name">app/services_db.py (중복 검증)</div>
        existing = repository.get_by_title(title)<br>
        <span class="keyword">if</span> existing:<br>
        &nbsp;&nbsp;<span class="keyword">raise</span> <span class="highlight">ValueError</span>(<span class="string">"이미 존재하는 제목입니다"</span>)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">2</span>
      <div class="code-block">
        <div class="file-name">app/main.py (예외 핸들러)</div>
        <span class="keyword">@app</span>.<span class="function">exception_handler</span>(ValueError)<br>
        <span class="keyword">def</span> <span class="function">value_error_handler</span>(request, exc):<br>
        &nbsp;&nbsp;<span class="keyword">return</span> JSONResponse(<br>
        &nbsp;&nbsp;&nbsp;&nbsp;status_code=<span class="highlight">400</span>,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;content={<span class="string">"error"</span>: str(exc)}<br>
        &nbsp;&nbsp;)
      </div>
    </div>
    <p class="hint">ValueError → 400 Bad Request로 자동 변환!</p>
  `,
  test_not_found: `
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">1</span>
      <div class="code-block">
        <div class="file-name">app/repository_db.py</div>
        item = self._db.query(ItemModel).filter(...).first()<br>
        <span class="keyword">if</span> <span class="keyword">not</span> item:<br>
        &nbsp;&nbsp;<span class="keyword">raise</span> <span class="highlight">HTTPException</span>(status_code=404)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">2</span>
      <div class="code-block">
        <div class="file-name">app/main.py (404 핸들러)</div>
        <span class="keyword">@app</span>.<span class="function">exception_handler</span>(<span class="highlight">404</span>)<br>
        <span class="keyword">def</span> <span class="function">not_found_handler</span>(request, exc):<br>
        &nbsp;&nbsp;<span class="keyword">return</span> JSONResponse(<br>
        &nbsp;&nbsp;&nbsp;&nbsp;status_code=404,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;content={<span class="string">"error"</span>: <span class="string">"리소스를 찾을 수 없습니다"</span>}<br>
        &nbsp;&nbsp;)
      </div>
    </div>
  `,
  test_validation: `
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">1</span>
      <div class="code-block">
        <div class="file-name">app/schemas.py (Pydantic 검증)</div>
        <span class="keyword">class</span> <span class="function">ItemCreate</span>(BaseModel):<br>
        &nbsp;&nbsp;title: str = Field(..., min_length=1) <span class="comment"># 필수!</span><br>
        &nbsp;&nbsp;description: Optional[str] = None
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #ef4444;">2</span>
      <div class="code-block">
        <div class="file-name">FastAPI 자동 검증</div>
        <span class="comment"># title 필드가 없으면 FastAPI가 자동으로 422 에러 반환</span><br>
        {<br>
        &nbsp;&nbsp;<span class="string">"detail"</span>: [{<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="string">"loc"</span>: [<span class="string">"body"</span>, <span class="string">"title"</span>],<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="string">"msg"</span>: <span class="string">"field required"</span><br>
        &nbsp;&nbsp;}]<br>
        }
      </div>
    </div>
    <p class="hint">Pydantic이 자동으로 422 Unprocessable Entity 반환!</p>
  `,

  // Step 6: 파일 업로드 코드 흐름
  upload_file: `
    <div class="flow-step">
      <span class="step-num" style="background: #14b8a6;">1</span>
      <div class="code-block">
        <div class="file-name">app/api/routes_upload.py (파일 검증)</div>
        <span class="keyword">def</span> <span class="function">validate_file</span>(file: <span class="highlight">UploadFile</span>):<br>
        &nbsp;&nbsp;file_ext = os.path.splitext(file.filename)[1].lower()<br>
        &nbsp;&nbsp;<span class="keyword">if</span> file_ext <span class="keyword">not in</span> ALLOWED_EXTENSIONS:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword">raise</span> HTTPException(status_code=400)
      </div>
    </div>
    <div class="flow-step">
      <span class="step-num" style="background: #14b8a6;">2</span>
      <div class="code-block">
        <div class="file-name">파일 저장 (청크 단위)</div>
        <span class="keyword">with</span> open(filepath, <span class="string">"wb"</span>) <span class="keyword">as</span> buffer:<br>
        &nbsp;&nbsp;<span class="keyword">while</span> <span class="keyword">True</span>:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;chunk = upload_file.file.read(<span class="highlight">8192</span>)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword">if</span> file_size > MAX_FILE_SIZE:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword">raise</span> HTTPException(status_code=413)
      </div>
    </div>
    <p class="hint">파일은 8KB씩 청크로 읽어서 저장 (메모리 효율적)</p>
  `,
  list_uploads: `
    <div class="flow-step">
      <span class="step-num" style="background: #14b8a6;">1</span>
      <div class="code-block">
        <div class="file-name">uploads 디렉토리 스캔</div>
        <span class="keyword">for</span> filename <span class="keyword">in</span> os.listdir(UPLOAD_DIR):<br>
        &nbsp;&nbsp;stat = os.stat(filepath)<br>
        &nbsp;&nbsp;files.append({<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="string">"filename"</span>: filename,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span class="string">"size"</span>: stat.st_size<br>
        &nbsp;&nbsp;})
      </div>
    </div>
  `,
  run_tests: `
    <div class="flow-step">
      <span class="step-num" style="background: #14b8a6;">1</span>
      <div class="code-block">
        <div class="file-name">터미널에서 실행</div>
        $ <span class="highlight">pytest tests/ -v</span><br>
        <br>
        tests/test_api.py::test_health_check <span class="string">PASSED</span><br>
        tests/test_api.py::test_create_item <span class="string">PASSED</span><br>
        tests/test_api.py::test_upload_file <span class="string">PASSED</span><br>
        <br>
        <span class="comment"># 커버리지 확인</span><br>
        $ <span class="highlight">pytest --cov=app tests/</span>
      </div>
    </div>
    <p class="hint">pytest는 자동으로 모든 test_*.py 파일을 실행합니다</p>
  `,
};

function showCodeFlow(action) {
  if (codeFlows[action]) {
    codeFlowEl.innerHTML = codeFlows[action];
  } else {
    codeFlowEl.innerHTML = '<p class="hint">이 액션의 코드 흐름 정보가 없습니다.</p>';
  }
}

// 버튼별 API 호출 정의 (라우터 → 서비스 → 저장소로 이어짐)
const api = {
  // ============================================================
  // Step 1: 메모리 저장소 (/api/...)
  // ============================================================
  health: () => fetchJson("/api/health"),
  list: () => fetchJson("/api/items"),
  create: () =>
    fetchJson("/api/items", {
      method: "POST",
      body: {
        title: titleEl.value,
        description: descriptionEl.value || null,
      },
    }),
  get: () => fetchJson(`/api/items/${idEl.value}`),
  update: () =>
    fetchJson(`/api/items/${idEl.value}`, {
      method: "PUT",
      body: {
        title: titleEl.value || null,
        description: descriptionEl.value || null,
        is_done: doneEl.checked,
      },
    }),
  delete: () => fetchJson(`/api/items/${idEl.value}`, { method: "DELETE" }),
  reset: () => fetchJson("/api/reset", { method: "POST" }),

  // ============================================================
  // Step 2: DB 저장소 (/api/v2/...)
  // 의존성 주입(Depends) + SQLite
  // ============================================================
  health_db: () => fetchJson("/api/v2/health"),
  list_db: () => fetchJson("/api/v2/items"),
  create_db: () =>
    fetchJson("/api/v2/items", {
      method: "POST",
      body: {
        title: titleEl.value,
        description: descriptionEl.value || null,
      },
    }),
  get_db: () => fetchJson(`/api/v2/items/${idEl.value}`),
  update_db: () =>
    fetchJson(`/api/v2/items/${idEl.value}`, {
      method: "PUT",
      body: {
        title: titleEl.value || null,
        description: descriptionEl.value || null,
        is_done: doneEl.checked,
      },
    }),
  delete_db: () => fetchJson(`/api/v2/items/${idEl.value}`, { method: "DELETE" }),
  reset_db: () => fetchJson("/api/v2/reset", { method: "POST" }),

  // ============================================================
  // Step 3: 인증 버전 (/api/v3/...)
  // JWT 토큰 + Depends(get_current_user)
  // ============================================================
  register: () =>
    fetchJson("/api/v3/register", {
      method: "POST",
      body: {
        username: getAuthUsername().value,
        password: getAuthPassword().value,
      },
    }),
  login: async () => {
    // 로그인은 form-data로 전송
    const formData = new URLSearchParams();
    formData.append("username", getAuthUsername().value);
    formData.append("password", getAuthPassword().value);
    const response = await fetch("/api/v3/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });
    const data = await response.json();
    if (response.ok) {
      accessToken = data.access_token;
      const statusEl = getTokenStatus();
      if (statusEl) {
        statusEl.textContent = `✅ 토큰: ${accessToken.substring(0, 20)}...`;
        statusEl.style.color = '#10b981';
      }
    }
    return data;
  },
  me: () => fetchJsonWithAuth("/api/v3/me"),
  list_auth: () => fetchJsonWithAuth("/api/v3/protected/items"),
  create_auth: () =>
    fetchJsonWithAuth("/api/v3/protected/items", {
      method: "POST",
      body: {
        title: titleEl.value,
        description: descriptionEl.value || null,
      },
    }),

  // ============================================================
  // Step 4: 비동기 + 백그라운드 (/api/v4/...)
  // ============================================================
  async_list: () => fetchJson("/api/v4/async/items"),
  async_create: () =>
    fetchJson("/api/v4/async/items", {
      method: "POST",
      body: {
        title: titleEl.value,
        description: descriptionEl.value || null,
      },
    }),
  sequential: () => fetchJson("/api/v4/async/sequential"),
  concurrent: () => fetchJson("/api/v4/async/concurrent"),
  bg_log: () =>
    fetchJson(`/api/v4/background/log?message=${encodeURIComponent("테스트 로그 메시지")}`, {
      method: "POST",
    }),
  bg_email: () =>
    fetchJson(`/api/v4/background/email?email=test@example.com&subject=테스트&body=테스트 이메일`, {
      method: "POST",
    }),

  // ============================================================
  // Step 5: 에러 핸들링
  // ============================================================
  test_duplicate: async () => {
    // 같은 타이틀로 두 번 생성해서 중복 에러 발생
    await fetchJsonWithAuth("/api/v3/items", {
      method: "POST",
      body: { title: "중복테스트", description: "첫 번째 생성" },
    });
    return fetchJsonWithAuth("/api/v3/items", {
      method: "POST",
      body: { title: "중복테스트", description: "두 번째 생성 (에러!)" },
    });
  },
  test_not_found: () => fetchJsonWithAuth("/api/v3/items/99999"),
  test_validation: () =>
    fetchJson("/api/items", {
      method: "POST",
      body: { description: "title 필드 없음!" },
    }),

  // ============================================================
  // Step 6: 파일 업로드 + 테스팅
  // ============================================================
  upload_file: async () => {
    const fileInput = document.getElementById("upload-file");
    if (!fileInput.files.length) {
      throw new Error("파일을 선택해주세요!");
    }
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    const response = await fetch("/api/v5/upload", {
      method: "POST",
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "업로드 실패");
    }
    
    return await response.json();
  },
  list_uploads: () => fetchJson("/api/v5/uploads"),
  clear_uploads: () => fetchJson("/api/v5/uploads/clear", { method: "DELETE" }),
  run_tests: async () => {
    return { 
      message: "브라우저에서 pytest를 직접 실행할 수 없습니다.",
      instruction: "터미널에서 'pytest tests/ -v' 명령을 실행하세요!",
      tip: "또는 'pytest tests/ -v --cov=app' 로 커버리지 확인"
    };
  },
};

// 공통 fetch 함수: JSON 요청/응답 처리
async function fetchJson(url, options = {}) {
  const init = {
    headers: { "Content-Type": "application/json" },
    ...options,
  };
  if (init.body && typeof init.body !== "string") {
    init.body = JSON.stringify(init.body);
  }

  const response = await fetch(url, init);
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw new Error(
      typeof data === "string" ? data : JSON.stringify(data, null, 2)
    );
  }
  return data;
}

// [Step 3] 인증 헤더 포함 fetch
async function fetchJsonWithAuth(url, options = {}) {
  if (!accessToken) {
    throw new Error("먼저 로그인하세요! (토큰이 없습니다)");
  }
  const init = {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${accessToken}`,  // JWT 토큰 추가
    },
    ...options,
  };
  if (init.body && typeof init.body !== "string") {
    init.body = JSON.stringify(init.body);
  }

  const response = await fetch(url, init);
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw new Error(
      typeof data === "string" ? data : JSON.stringify(data, null, 2)
    );
  }
  return data;
}

// 화면에 결과를 보기 좋게 출력
function renderOutput(data) {
  outputEl.textContent =
    typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

// 오류 출력
function renderError(error) {
  outputEl.textContent = `오류: ${error.message}`;
}

// 버튼 이벤트 연결
function setupButtons() {
  document.querySelectorAll("button[data-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.action;
      // action: health / create / list / get / update / delete / reset
      outputEl.textContent = "요청 중...";
      showCodeFlow(action);  // 코드 흐름 표시
      try {
        const result = await api[action]();
        renderOutput(result);
      } catch (error) {
        renderError(error);
      }
    });
  });
}

setupButtons();
